import operator
import os
from functools import wraps
from typing import List, Optional as Opt, Union

from moviepy.editor import AudioFileClip, VideoClip

import mugen.location_utility as loc_util
import mugen.utility as util
import mugen.video.io as v_io
import mugen.video.sizing as v_sizing
import mugen.video.effects as v_effects
from mugen.mixins.Taggable import Taggable
from mugen.utility import ensure_json_serializable
from mugen.video.VideoSegment import VideoSegment
from mugen.video.VideoWriter import VideoWriter
from mugen.video.io import SubtitleTrack
from mugen.video.sizing import Dimensions
from mugen.video.utility import CompositeVideoClip

SEGMENTS_DIRECTORY = 'video_segments'
REJECTED_SEGMENTS_DIRECTORY = 'rejected_video_segments'


def requires_video_segments(func):
    """
    Decorator returns None if there are no video segments
    """
    @wraps(func)
    def _requires_video_segments(self, *args, **kwargs):
        if not self.video_segments:
            raise ValueError("Music video has no video segments.")

        return func(self, *args, **kwargs)
    return _requires_video_segments


class MusicVideo(Taggable):
    """
    A video composed of video segments and overlaid audio

    Attributes
    ----------
    writer
        Wrapper for writing VideoClips to video files

    meta
        Json serializable dictionary with extra metadata
    """
    audio_file: Opt[str]
    video_segments: List[VideoSegment]
    writer: VideoWriter
    _dimensions: Opt[Dimensions]
    aspect_ratio: Opt[float]

    meta: dict

    @ensure_json_serializable('meta')
    def __init__(self, video_segments: List[VideoSegment], audio_file: Opt[str] = None, *,
                 dimensions: Opt[Dimensions] = None, aspect_ratio: Opt[float] = None, **kwargs):
        """
        Parameters
        ----------
        audio_file
            The audio file to use for the music video.
            If no audio file is provided, the original audio from the video segments will be used

        video_segments
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
        self.video_segments = video_segments
        self._dimensions = dimensions
        self.aspect_ratio = aspect_ratio
        self.writer = VideoWriter()

        # Optional Parameters
        self.meta = {}

    """ PROPERTIES """

    @property
    def dimensions(self) -> Dimensions:
        return self._dimensions or self._calculate_dimensions(self.aspect_ratio)

    @dimensions.setter
    def dimensions(self, value):
        self._dimensions = value

    @property
    def cut_locations(self) -> List[float]:
        """
        Returns
        -------
        Locations in the music video where a cut between video segments occurs (sec)
        """
        return loc_util.locations_from_intervals(self.cut_intervals)

    @property
    def cut_intervals(self) -> List[float]:
        """
        Returns
        -------
        Intervals between each cut location (sec)
        """
        return [segment.duration for segment in self.video_segments]

    """ METHODS """

    @requires_video_segments
    def _calculate_dimensions(self, aspect_ratio: Opt[float] = None) -> Union[Dimensions, None]:
        """
        Returns
        -------
        The largest dimensions available for the specified aspect ratio
        """
        if aspect_ratio:
            dimensions = v_sizing.largest_dimensions_for_aspect_ratio(
                [segment.dimensions for segment in self.video_segments], aspect_ratio)
        else:
            dimensions = max([segment.dimensions for segment in self.video_segments],
                             key=operator.attrgetter('resolution'))

        return dimensions

    @requires_video_segments
    def compose(self) -> VideoClip:
        """
        Composes the music video into a VideoClip
        """
        video_segments = [segment.crop_scale(self.dimensions) for segment in self.video_segments]
        video_segments = [segment.compose() for segment in video_segments]

        # Add buffers for crossfaded video segments
        buffered_video_segments = []
        for index, segment in enumerate(video_segments[:-1]):
            buffered_video_segments.append(segment)
            next_segment = video_segments[index + 1]

            for effect in next_segment.effects:
                if isinstance(effect, v_effects.CrossFade):
                    buffer = VideoSegment(segment.video_file)
                    buffer = buffer.subclip(segment.source_end_time, segment.source_end_time + effect.duration)
                    buffer = buffer.set_audio(buffer.audio.audio_fadeout(effect.duration))
                    buffered_video_segments.append(buffer)
        buffered_video_segments.append(video_segments[-1])

        video_segments = buffered_video_segments

        # Build composite video
        composite_video_segments = [video_segments[0]]
        for index, segment in enumerate(video_segments[1:]):
            # Start current segment where previous segment ends in composite video
            previous_segment = composite_video_segments[index]
            segment = segment.set_start(previous_segment.end)

            # Apply any crossfade for the current segment
            for effect in segment.effects:
                if isinstance(effect, v_effects.CrossFade):
                    segment = segment.set_start(previous_segment.end - effect.duration)
                    segment = segment.crossfadein(effect.duration)
                    segment = segment.set_audio(segment.audio.audio_fadein(effect.duration))

            composite_video_segments.append(segment)

        music_video = CompositeVideoClip(composite_video_segments)

        if self.audio_file:
            music_video.audio = AudioFileClip(self.audio_file)

        return music_video

    @requires_video_segments
    def write_to_video_file(self, output_path: str):
        """
        writes the music video to a video file
        
        Parameters
        ----------        
        output_path 
            Path for the video file

        Use this method over moviepy's write_videofile to preserve the audio file's codec and bitrate.
        """
        audio = self.audio_file or True
        composed_music_video = self.compose()

        # Must use separate temporary file to properly write subtitle/audio tracks via ffmpeg
        temp_output_path = self.writer.write_video_clip_to_file(composed_music_video, audio=audio, verbose=False)

        # Add helpful subtitle/audio tracks to video file
        self._add_auxiliary_tracks(temp_output_path, output_path)

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
        numbers = [index for index, _ in enumerate(self.video_segments)]
        locations = self.cut_locations
        intervals = self.cut_intervals

        subtitle_track_segment_numbers = SubtitleTrack.create(numbers, 'segment_numbers', durations=intervals)
        subtitle_track_segment_locations = SubtitleTrack.create(locations, 'segment_locations', durations=intervals)
        subtitle_track_segment_durations = SubtitleTrack.create(intervals, 'segment_intervals', durations=intervals)

        subtitle_tracks = [subtitle_track_segment_numbers, subtitle_track_segment_locations,
                           subtitle_track_segment_durations]
        v_io.add_tracks_to_video(video_file, output_path, subtitle_tracks=subtitle_tracks)

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
        util.recreate_dir(directory)

        video_segments = [segment.crop_scale(self.dimensions) for segment in self.video_segments]

        self.writer.write_video_clips_to_directory(video_segments, directory)
