import operator
import os
from functools import wraps
from typing import List, Optional, Union

from moviepy.editor import AudioFileClip, VideoClip

import mugen.video.effects as video_effects
import mugen.video.sizing as video_sizing
from mugen.events import EventList
from mugen.mixins.Persistable import Persistable
from mugen.utilities import location, system
from mugen.utilities.system import use_temporary_file_fallback
from mugen.utilities.validation import ensure_json_serializable
from mugen.video.cuts import Cut
from mugen.video.io import tracks
from mugen.video.io.tracks import SubtitleTrack
from mugen.video.io.VideoWriter import VideoWriter
from mugen.video.moviepy.CompositeVideoClip import CompositeVideoClip
from mugen.video.segments.Segment import Segment
from mugen.video.sizing import Dimensions

SEGMENTS_DIRECTORY = "video_segments"
REJECTED_SEGMENTS_DIRECTORY = "rejected_video_segments"


def requires_video_segments(func):
    """
    Decorator raises Error if there are no video segments
    """

    @wraps(func)
    def _requires_video_segments(self, *args, **kwargs):
        if not self.segments:
            raise ValueError(
                f"MusicVideo's {func} method requires one or more segments."
            )

        return func(self, *args, **kwargs)

    return _requires_video_segments


class MusicVideo(Persistable):
    """
    A video composed of video segments and overlaid audio

    Attributes
    ----------
    writer
        Wrapper for writing VideoClips to video files

    meta
        Json serializable dictionary with extra metadata
    """

    audio_file: Optional[str]
    segments: List[Segment]
    writer: VideoWriter
    _dimensions: Optional[Dimensions]
    aspect_ratio: Optional[float]

    meta: dict

    @ensure_json_serializable("meta")
    def __init__(
        self,
        segments: List[Segment],
        audio_file: Optional[str] = None,
        *,
        dimensions: Optional[Dimensions] = None,
        aspect_ratio: Optional[float] = None,
        **kwargs,
    ):
        """
        Parameters
        ----------
        audio_file
            The audio file to use for the music video.
            If no audio file is provided, the original audio from the video segments will be used

        segments
            Video segments composing the music video

        dimensions
            Width and height for the music video.
            If no dimensions or aspect ratio are specified,
            the largest dimensions among the video segments will be used.

        aspect_ratio
            Aspect ratio for the music video (Overruled by dimensions)
        """
        super().__init__(**kwargs)

        # Required Parameters
        self.audio_file = audio_file
        self.segments = segments
        self._dimensions = dimensions
        self.aspect_ratio = aspect_ratio
        self.writer = VideoWriter()

        # Optional Parameters
        self.meta = {}

    """ PROPERTIES """

    @property
    def duration(self) -> int:
        return sum([segment.duration for segment in self.segments])

    @property
    def dimensions(self) -> Dimensions:
        return self._dimensions or self._calculate_dimensions()

    @dimensions.setter
    def dimensions(self, value):
        self._dimensions = value

    @property
    def cuts(self) -> EventList:
        durations = [segment.duration for segment in self.segments]
        locations = location.locations_from_intervals(durations)
        return EventList(
            [Cut(location) for location in locations[:-1]], end=locations[-1]
        )

    """ METHODS """

    @requires_video_segments
    def _calculate_dimensions(self) -> Dimensions:
        """
        Returns
        -------
        The largest dimensions available for the music video's aspect ratio
        """
        if self.aspect_ratio:
            dimensions = video_sizing.largest_dimensions_for_aspect_ratio(
                [segment.dimensions for segment in self.segments], self.aspect_ratio
            )
        else:
            dimensions = max(
                [segment.dimensions for segment in self.segments],
                key=operator.attrgetter("resolution"),
            )

        return dimensions

    @requires_video_segments
    def compose(self) -> VideoClip:
        """
        Composes the music video into a VideoClip
        """
        segments = [segment.crop_scale(self.dimensions) for segment in self.segments]
        segments = [segment.apply_effects() for segment in segments]

        # Add buffers for crossfaded video segments
        buffered_video_segments = []
        for index, segment in enumerate(segments):
            buffered_video_segments.append(segment)

            if index == len(segments) - 1:
                continue

            next_segment = segments[index + 1]

            for effect in next_segment.effects:
                if isinstance(effect, video_effects.CrossFade):
                    buffer = segment.trailing_buffer(effect.duration)
                    if buffer.audio:
                        buffer = buffer.set_audio(
                            buffer.audio.audio_fadeout(effect.duration)
                        )
                    buffered_video_segments.append(buffer)

        segments = buffered_video_segments

        # Build composite video
        composite_video_segments = [segments[0]]
        for index, segment in enumerate(segments[1:]):
            # Start current segment where previous segment ends in composite video
            previous_segment = composite_video_segments[index]
            segment = segment.set_start(previous_segment.end)

            # Apply any crossfade for the current segment
            for effect in segment.effects:
                if isinstance(effect, video_effects.CrossFade):
                    segment = segment.set_start(previous_segment.end - effect.duration)
                    segment = segment.crossfadein(effect.duration)
                    if segment.audio:
                        segment = segment.set_audio(
                            segment.audio.audio_fadein(effect.duration)
                        )

            composite_video_segments.append(segment)

        music_video = CompositeVideoClip(composite_video_segments)

        if self.audio_file:
            music_video.audio = AudioFileClip(self.audio_file)

        return music_video

    @requires_video_segments
    @use_temporary_file_fallback("output_path", VideoWriter.VIDEO_EXTENSION)
    def write_to_video_file(
        self,
        output_path: Optional[str] = None,
        *,
        audio: Optional[Union[bool, str]] = None,
        add_auxiliary_tracks: bool = True,
        verbose: bool = False,
        show_progress: bool = True,
        **kwargs,
    ):
        """
        writes the music video to a video file

        Parameters
        ----------
        output_path
            Path for the video file

        audio
            Audio for the music video. Can be True to enable, False to disable, an external audio file,
            or None to automatically set the value.

        add_auxiliary_tracks
            Whether or not helpful auxiliary subtitle tracks should be included.

        verbose
            Whether output to stdout should include extra information during writing

        show_progress
            Whether to output progress information to stdout

        Use this method over moviepy's write_videofile to preserve the audio file's codec and bitrate.
        """
        if audio is None:
            audio = self.audio_file or True
        composed_music_video = self.compose()

        if add_auxiliary_tracks:
            temp_output_path = self.writer.write_video_clip_to_file(
                composed_music_video,
                audio=audio,
                verbose=verbose,
                show_progress=show_progress,
                **kwargs,
            )
            # Add helpful subtitle/audio tracks to video file
            self._add_auxiliary_tracks(temp_output_path, output_path)
        else:
            self.writer.write_video_clip_to_file(
                composed_music_video,
                output_path,
                audio=audio,
                verbose=verbose,
                show_progress=show_progress,
                **kwargs,
            )

        return output_path

    def _add_auxiliary_tracks(self, video_file: str, output_path: str):
        """
        Adds metadata subtitle/audio tracks to the music video

        Parameters
        ----------
        video_file
            The temporary music video output file

        output_path
            The final music video output file with added auxiliary tracks
        """
        # Subtitle Tracks
        cuts = self.cuts
        numbers = [index for index, _ in enumerate(self.segments)]
        locations = [round(location, 2) for location in cuts.segment_locations]
        durations = cuts.segment_durations
        rounded_durations = [round(interval, 2) for interval in cuts.segment_durations]

        subtitle_track_segment_numbers = SubtitleTrack.create(
            numbers, "segment_numbers", durations=durations
        )
        subtitle_track_segment_locations = SubtitleTrack.create(
            locations, "segment_locations_seconds", durations=durations
        )
        subtitle_track_segment_durations = SubtitleTrack.create(
            rounded_durations, "segment_durations_seconds", durations=durations
        )

        subtitle_tracks = [
            subtitle_track_segment_numbers,
            subtitle_track_segment_locations,
            subtitle_track_segment_durations,
        ]
        tracks.add_tracks_to_video(
            video_file, output_path, subtitle_tracks=subtitle_tracks
        )

    @requires_video_segments
    def write_video_segments(self, directory: str):
        """
        Saves video_segments or video_segment_rejects to video files in the specified directory

        Parameters
        ----------
        directory
            location to save video segments
        """
        directory = os.path.join(directory, SEGMENTS_DIRECTORY)
        system.recreate_directory(directory)

        video_segments = [
            segment.crop_scale(self.dimensions) for segment in self.segments
        ]

        self.writer.write_video_clips_to_directory(video_segments, directory)
