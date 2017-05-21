import os

from typing import List, Optional as Opt, Tuple

import moviepy.editor as moviepy
from moviepy.editor import AudioFileClip, VideoClip

import mugen.utility as util
import mugen.location_utility as loc_util
import mugen.video.sizing as v_sizing

from mugen.utility import ensure_json_serializable
from mugen.mixins.Filterable import Filter
from mugen.video.VideoSegment import VideoSegmentList
from mugen.video.VideoWriter import VideoWriter
from mugen.video.sizing import Dimensions

SEGMENTS_DIRECTORY = 'video_segments'
REJECTED_SEGMENTS_DIRECTORY = 'rejected_video_segments'


class MusicVideo:
    """
    A video composed of video segments and overlaid audio

    Attributes
    ----------
    audio_file 
        Audio for the music video. 
        
    video_segments 
        Video segments composing the music video
        
    source_videos 
        Videos used to sample video_segments
        
    rejected_video_segments 
        Video segments rejected from the music video
        
    video_filters
        names of video filters that each segment in the music video passed.
        
    meta
        Json serializable dictionary with metadata describing the music video
    """
    audio_file: str
    video_segments: VideoSegmentList
    writer: VideoWriter

    source_videos: VideoSegmentList
    rejected_video_segments: VideoSegmentList
    video_filters: List[Filter]
    meta: dict

    @ensure_json_serializable('meta')
    def __init__(self, audio_file: str, video_segments: VideoSegmentList, *,
                 source_videos: VideoSegmentList = None, rejected_video_segments: VideoSegmentList = None,
                 video_filters: Opt[List[Filter]] = None, meta: Opt[dict] = None):
        # Required Parameters
        self.audio_file = audio_file
        self.video_segments = video_segments
        self.writer = VideoWriter()

        # Optional Parameters
        self.source_videos = source_videos or VideoSegmentList()
        self.rejected_video_segments = rejected_video_segments or VideoSegmentList()
        self.video_filters = video_filters or []
        self.meta = meta or {}

    """ PROPERTIES """

    @property
    def duration(self) -> float:
        return sum(self.video_segments.durations)

    @property
    def dimensions(self) -> Opt[Dimensions]:
        """
        Returns
        -------
        The largest dimensions from video_segments
        """
        return v_sizing.largest_dimensions(self.video_segments.dimensions, default=None)

    @property
    def aspect_ratio(self) -> float:
        return self.dimensions.aspect_ratio

    @property
    def fps(self) -> int:
        return max(self.video_segments.fpses)

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
        return self.video_segments.durations

    """ METHODS """

    def _determine_dimensions(self, dimensions: Opt[Tuple[int, int]] = None,
                              aspect_ratio: Opt[float] = None) -> Dimensions:
        if dimensions:
            dimensions = Dimensions(*dimensions)
        elif aspect_ratio:
            dimensions = v_sizing.largest_dimensions_for_aspect_ratio(self.video_segments.dimensions, aspect_ratio,
                                                                      default=None)
        else:
            dimensions = self.dimensions

        return dimensions

    def compose(self, *, dimensions: Opt[Tuple[int, int]] = None, aspect_ratio: Opt[float] = None,
                use_original_audio: bool = False) -> VideoClip:
        """
        Composes the music video into a VideoClip

        Parameters
        ----------        
        dimensions 
            Width and height for the music video
            
        aspect_ratio
            Aspect ratio for the music video (Overruled by dimensions)
            
        use_original_audio
            Whether or not to use the original audio from video_segments for the music video, instead of the audio_file
        """
        dimensions = self._determine_dimensions(dimensions, aspect_ratio)

        video_segments = [segment.crop_scale(dimensions) for segment in self.video_segments]
        music_video = moviepy.concatenate_videoclips(video_segments, method="compose")
        if not use_original_audio:
            music_video.set_audio(AudioFileClip(self.audio_file))

        return music_video

    def write_to_video_file(self, output_path: str, *, dimensions: Opt[Tuple[int, int]] = None,
                            aspect_ratio: Opt[float] = None, use_original_audio: bool = False,
                            precomposed_music_video: Opt[VideoClip] = None):
        """
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

        self.writer.write_video_clip_to_file(composed_music_video, output_path, audio=audio, verbose=False)

    def save_video_segments(self, directory: str, *, rejected=False, dimensions: Opt[Tuple[int, int]] = None,
                            aspect_ratio: Opt[float] = None):
        """
        Saves video_segments or video_segment_rejects to video files in the specified directory
        
        Parameters
        ----------
        directory
            location to save video segments
            
        rejected
            False saves the music video's segments, True saves the music video's rejected segments
                        
        dimensions 
            Width and height for the video segments.
            
        aspect_ratio
            Aspect ratio for the video segments (overruled by dimensions)
            
        If no dimensions or aspect ratio are specified, 
        the largest dimensions found among the video segments will be used.
        """
        if rejected:
            video_segments = self.rejected_video_segments
            directory = os.path.join(directory, REJECTED_SEGMENTS_DIRECTORY)
            util.recreate_dir(directory)
        else:
            video_segments = self.video_segments
            directory = os.path.join(directory, SEGMENTS_DIRECTORY)
            util.recreate_dir(directory)

        dimensions = self._determine_dimensions(dimensions, aspect_ratio)
        video_segments = [segment.crop_scale(dimensions) for segment in video_segments]

        self.writer.write_video_clips_to_directory(video_segments, directory)

    def write_to_spec_file(self, filename):
        return

    def to_spec(self):
        return

    @classmethod
    def from_spec(cls, spec):
        return


