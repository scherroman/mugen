import operator
import os
from typing import List, Optional as Opt, Tuple

import moviepy.editor as moviepy
from moviepy.editor import AudioFileClip, VideoClip

import mugen.location_utility as loc_util
import mugen.utility as util
import mugen.video.io as v_io
import mugen.video.sizing as v_sizing
from mugen.mixins.Taggable import Taggable
from mugen.utility import ensure_json_serializable
from mugen.video.VideoSegment import VideoSegmentList, VideoSegment
from mugen.video.VideoWriter import VideoWriter
from mugen.video.io import SubtitleTrack
from mugen.video.sizing import Dimensions

SEGMENTS_DIRECTORY = 'video_segments'
REJECTED_SEGMENTS_DIRECTORY = 'rejected_video_segments'


class MusicVideo(Taggable):
    """
    A video composed of video segments and overlaid audio

    Attributes
    ----------
    audio_file 
        The audio file to use for the music video. 
        
    video_segments 
        Video segments composing the music video

    meta
        Json serializable dictionary with extra metadata
    """
    audio_file: str
    video_segments: VideoSegmentList
    writer: VideoWriter

    meta: dict

    @ensure_json_serializable('meta')
    def __init__(self, audio_file: str, video_segments: List[VideoSegment], **kwargs):
        super().__init__(**kwargs)

        # Required Parameters
        self.audio_file = audio_file
        self.video_segments = VideoSegmentList(video_segments)
        self.writer = VideoWriter()

        # Optional Parameters
        self.meta = {}

    """ PROPERTIES """

    @property
    def duration(self) -> float:
        return sum([segment.duration for segment in self.video_segments])

    @property
    def fps(self) -> int:
        return max([segment.fps for segment in self.video_segments], default=None)

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

    def calculate_dimensions(self, aspect_ratio: Opt[float] = None) -> Dimensions:
        """
        Returns
        -------
        The largest dimensions available for the specified aspect ratio
        """
        if aspect_ratio:
            dimensions = v_sizing.largest_dimensions_for_aspect_ratio(
                [segment.dimensions for segment in self.video_segments], aspect_ratio, default=None)
        else:
            dimensions = max([segment.dimensions for segment in self.video_segments],
                             key=operator.attrgetter('resolution'), default=None)

        return dimensions

    def compose(self, *, dimensions: Opt[Tuple[int, int]] = None, aspect_ratio: Opt[float] = None,
                use_original_audio: bool = False) -> VideoClip:
        """
        Composes the music video into a VideoClip

        Parameters
        ----------        
        dimensions 
            Width and height for the music video
            If no dimensions are provided, the largest dimensions available for the specified aspect_ratio will be used
            
        aspect_ratio
            Aspect ratio for the music video (Overruled by dimensions)
            
        use_original_audio
            Whether or not to use the original audio from video_segments for the music video, instead of the audio_file
        """
        if dimensions is None:
            dimensions = self.calculate_dimensions(aspect_ratio)

        video_segments = [segment.crop_scale(dimensions) for segment in self.video_segments]
        music_video = moviepy.concatenate_videoclips(video_segments, method="compose")
        if not use_original_audio:
            music_video.set_audio(AudioFileClip(self.audio_file))

        return music_video

    def write_to_video_file(self, output_path: str, *, dimensions: Opt[Tuple[int, int]] = None,
                            aspect_ratio: Opt[float] = None, use_original_audio: bool = False,
                            precomposed_music_video: Opt[VideoClip] = None):
        """
        writes the music video to a video file
        
        Parameters
        ----------        
        output_path 
            Path for the video file
                
        dimensions 
            Width and height for the music video.
            
        aspect_ratio
            Aspect ratio for the music video (overruled by dimensions)
            
        use_original_audio
            Whether or not to use the original audio from video_segments for the music video, instead of the audio_file
            
        precomposed_music_video 
            A pre-composed music video to write
            
        If no dimensions or aspect ratio are specified, 
        the largest dimensions found among the video segments will be used.
        
        Use this method over moviepy's write_videofile to preserve the audio file's codec and bitrate.
        """
        audio = self.audio_file if not use_original_audio else True

        if precomposed_music_video:
            composed_music_video = precomposed_music_video
        else:
            composed_music_video = self.compose(dimensions=dimensions, aspect_ratio=aspect_ratio,
                                                use_original_audio=use_original_audio)

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

    def write_video_segments(self, directory: str, *, dimensions: Opt[Tuple[int, int]] = None,
                             aspect_ratio: Opt[float] = None):
        """
        Saves video_segments or video_segment_rejects to video files in the specified directory
        
        Parameters
        ----------
        directory
            location to save video segments
                             
        dimensions 
            Width and height for the video segments.
            
        aspect_ratio
            Aspect ratio for the video segments (overruled by dimensions)
            
        If no dimensions or aspect ratio are specified, 
        the largest dimensions found among the video segments will be used.
        """
        directory = os.path.join(directory, SEGMENTS_DIRECTORY)
        util.recreate_dir(directory)

        if dimensions is None:
            dimensions = self.calculate_dimensions(aspect_ratio)
        video_segments = [segment.crop_scale(dimensions) for segment in self.video_segments]

        self.writer.write_video_clips_to_directory(video_segments, directory)

    def load_from_spec_file(self, spec_file):
        return

    def write_to_spec_file(self, spec_file):
        return

    def to_spec(self):
        return

    @classmethod
    def from_spec(cls, spec):
        return


