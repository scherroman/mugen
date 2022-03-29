import operator
import os
from functools import wraps
from typing import List, Optional

from moviepy.editor import AudioFileClip, VideoClip

from mugen.events.Event import Event
from mugen.events.EventList import EventList
from mugen.mixins.Persistable import Persistable
from mugen.utilities import location, system
from mugen.utilities.system import use_temporary_file_fallback
from mugen.video import sizing, transformation
from mugen.video.events import Cut
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
    dimensions
        Width and height for the music video.
        If no dimensions or aspect ratio are specified,
        the largest dimensions among the video segments will be used.

    aspect_ratio
        Aspect ratio for the music video (Overruled by dimensions)

    writer
        Wrapper for writing VideoClips to video files
    """

    audio_file: Optional[str]
    segments: List[Segment]
    rejected_segments: List[Segment]
    writer: VideoWriter
    _dimensions: Optional[Dimensions]
    aspect_ratio: Optional[float]
    events: Optional[List[Event]]

    def __init__(
        self,
        segments: List[Segment],
        audio_file: Optional[str] = None,
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
        """
        super().__init__(**kwargs)

        # Required Parameters
        self.audio_file = audio_file
        self.segments = segments
        self._dimensions = None
        self.aspect_ratio = None
        self.writer = VideoWriter()
        self._events = None

    """ PROPERTIES """

    @property
    def duration(self) -> int:
        return sum([segment.duration for segment in self.segments])

    @property
    def dimensions(self) -> Dimensions:
        return self._dimensions or self._calculate_dimensions()

    @dimensions.setter
    def dimensions(self, value: Dimensions):
        self._dimensions = value

    @property
    def events(self) -> EventList:
        return self._events or self.cuts

    @events.setter
    def events(self, value: EventList):
        self._events = value

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
            dimensions = sizing.largest_dimensions_for_aspect_ratio(
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
        Composes the music video into a single VideoClip
        """
        segments = [
            transformation.crop_scale(segment, self.dimensions)
            for segment in self.segments
        ]
        segments = [transformation.apply_effects(segment) for segment in segments]
        segments = transformation.add_effect_buffers(segments)

        # Build composite video
        composite_video_segments = [segments[0]]
        for index, segment in enumerate(segments[1:]):
            # Start current segment where previous segment ends in composite video
            previous_segment = composite_video_segments[index]
            segment = segment.set_start(previous_segment.end)
            segment = transformation.apply_contextual_effects(segment, previous_segment)
            composite_video_segments.append(segment)

        music_video = CompositeVideoClip(composite_video_segments)

        if self.audio_file:
            music_video.audio = AudioFileClip(self.audio_file)

        return music_video

    @requires_video_segments
    @use_temporary_file_fallback("output_path", VideoWriter.DEFAULT_VIDEO_EXTENSION)
    def write_to_video_file(
        self, output_path: Optional[str] = None, *, show_progress: bool = True
    ):
        """
        writes the music video to a video file

        Parameters
        ----------
        output_path
            Path for the video file

        show_progress
            Whether to output progress information to stdout

        Use this method over moviepy's write_videofile to preserve the audio file's codec and bitrate.
        """
        composed_music_video = self.compose()

        temp_output_path = self.writer.write_video_clip_to_file(
            composed_music_video,
            audio=self.audio_file if self.audio_file else True,
            show_progress=show_progress,
        )
        self._add_subtitle_tracks(temp_output_path, output_path)

        return output_path

    def _add_subtitle_tracks(self, video_file: str, output_path: str):
        """
        Adds metadata subtitle/audio tracks to the music video

        Parameters
        ----------
        video_file
            The current music video output file

        output_path
            The final music video output file path with added auxiliary tracks
        """
        event_subtitles = [
            f"{event.index_repr(index)}".replace("<", "").replace(">", "")
            for index, event in enumerate(self.events)
        ]
        events_subtitle_track = SubtitleTrack.create(
            "events", event_subtitles, self.events.locations
        )
        tracks.add_subtitle_tracks_to_video(
            video_file, [events_subtitle_track], output_path
        )

    @requires_video_segments
    def write_video_segments(self, directory: str, show_progress: bool = True):
        """
        Saves the music video's individual video segments to video files in the specified directory

        Parameters
        ----------
        directory
            location to save video segments

        show_progress
            Whether to output progress information to stdout
        """
        self._write_video_segments(
            self.segments,
            os.path.join(directory, SEGMENTS_DIRECTORY),
            show_progress=show_progress,
        )

    def write_rejected_video_segments(self, directory: str, show_progress: bool = True):
        """
        Saves the music video's rejected video segments to video files in the specified directory

        Parameters
        ----------
        directory
            location to save video segments

        show_progress
            Whether to output progress information to stdout
        """
        failed_filter_names = {
            filter.name
            for segment in self.rejected_segments
            for filter in segment.failed_filters
        }
        rejected_video_segments_by_filter_name = dict().fromkeys(
            failed_filter_names, []
        )
        for segment in self.rejected_segments:
            for filter in segment.failed_filters:
                rejected_video_segments_by_filter_name[filter.name].append(segment)

        for filter_name, segments in rejected_video_segments_by_filter_name.items():
            self._write_video_segments(
                segments,
                os.path.join(directory, REJECTED_SEGMENTS_DIRECTORY, filter_name),
                show_progress=show_progress,
            )

    def _write_video_segments(
        self, segments: List[Segment], directory: str, show_progress: bool = True
    ):
        """
        Saves video segments to the specified directory

        Parameters
        ----------
        segments
            video segments to save

        directory
            location to save video segments
        """
        system.recreate_directory(directory)
        segments = [
            transformation.crop_scale(segment, self.dimensions) for segment in segments
        ]
        self.writer.write_video_clips_to_directory(
            segments, directory, file_extension=".mp4", show_progress=show_progress
        )
