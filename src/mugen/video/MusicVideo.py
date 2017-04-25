import os

from typing import List, Optional as Opt, Tuple, Union

import moviepy.editor as moviepy
from moviepy.editor import AudioFileClip, VideoClip

import mugen.utility as util
import mugen.audio.constants as ac
import mugen.video.constants as vc
import mugen.video.sizing as v_sizing

from mugen.utility import ensure_json_serializable, temp_file_enabled
from mugen.mixins.Taggable import Taggable
from mugen.mixins.Filterable import Filter
from mugen.video.VideoSegment import VideoSegment
from mugen.video.sizing import Dimensions


class MusicVideo(Taggable):
    """
    A video composed of video segments and overlaid audio.

    Attributes:
        video_segments: Video segments composing the music video
        
        audio_file: Audio for the music video. If None, audio from video_segments will be used instead.
        
        source_videos: Videos used to sample video segments from
        rejected_video_segments: Video segments rejected from the music video
        video_segment_trait_filters: 
        meta: Json serializable dictionary with metadata describing the music video
        
    If audio_file is given, its existing audio codec and bitrate will be used.
    """
    video_segments: List[VideoSegment]

    audio_file: Opt[str] = None

    source_videos: List[VideoSegment]
    rejected_video_segments: List[VideoSegment]
    video_segment_filters: List[Filter]
    meta: dict

    @ensure_json_serializable('meta')
    def __init__(self, video_segments: List[VideoSegment], audio_file: Opt[str] = None,
                 source_videos: Opt[List[VideoSegment]] = None, rejected_video_segments: Opt[List[VideoSegment]] = None,
                 video_segment_filters: Opt[List[Filter]] = None, meta: Opt[dict] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Required Parameters
        self.video_segments = video_segments

        # Optional Parameters
        self.audio_file = audio_file
        self.source_videos = source_videos or []
        self.rejected_video_segments = rejected_video_segments or []
        self.video_segment_filters = video_segment_filters or []
        self.meta = meta or {}

    """ PROPERTIES """

    @property
    def duration(self) -> float:
        return sum([segment.duration for segment in self.video_segments])

    @property
    def dimensions(self) -> Opt[Dimensions]:
        """
        Returns: _dimensions if set, or calculates them from dimensions of video segments and _aspect_ratio
        """
        return v_sizing.largest_width_and_height_for_dimensions([segment.dimensions for segment in self.video_segments],
                                                                default=None)

    @property
    def aspect_ratio(self) -> float:
        return self.dimensions.aspect_ratio

    @property
    def fps(self) -> int:
        return max([segment.fps for segment in self.video_segments])

    @property
    def cut_locations(self) -> List[float]:
        """
        Returns: Locations in the music video where a cut between video segments occurs (sec)
        """
        return util.locations_from_intervals(self.cut_intervals)

    @property
    def cut_intervals(self) -> List[float]:
        """
        Returns: Intervals between each cut location (sec)
        """
        return [segment.duration for segment in self.video_segments]

    """ METHODS """

    def _determine_dimensions(self, dimensions: Opt[Tuple[int, int]] = None,
                              aspect_ratio: Opt[float] = None) -> Dimensions:
        if dimensions:
            dimensions = Dimensions(*dimensions)
        elif aspect_ratio:
            dimensions = v_sizing.largest_dimensions_for_aspect_ratio(
                [segment.dimensions for segment in self.video_segments],
                aspect_ratio, default=None)
        else:
            dimensions = self.dimensions

        return dimensions

    def compose(self, dimensions: Opt[Tuple[int, int]] = None, aspect_ratio: Opt[float] = None) -> VideoClip:
        """
        Returns a composed VideoClip of the music video
        
        Attributes:
            dimensions: Width and height for the music video
            aspect_ratio: Aspect ratio for the music video (Overruled by dimensions)
        """
        dimensions = self._determine_dimensions(dimensions, aspect_ratio)

        video_segments = [segment.crop_scale(dimensions) for segment in self.video_segments]
        music_video = moviepy.concatenate_videoclips(video_segments, method="compose")
        if self.audio_file:
            music_video.set_audio(AudioFileClip(self.audio_file))

        return music_video

    def write_to_video_file(self, output_path: str, composed_music_video: Opt[VideoClip] = None,
                            dimensions: Opt[Tuple[int, int]] = None, aspect_ratio: Opt[float] = None,
                            codec: Opt[str] = None, crf: Opt[int] = None, audio_codec: Opt[str] = None,
                            audio_bitrate: Opt[str] = None, ffmpeg_params: Opt[List[str]] = None):
        """
        Args:
            output_path: Path for the video file
            composed_music_video: A pre-composed music video to write
            dimensions: Width and height for the music video
            aspect_ratio: Aspect ratio for the music video (overruled by dimensions)
            codec: video codec to use when writing the music video to file. Default libx264
            crf: constant rate factor (quality) for the music video (0 - 51)
            audio_codec: audio codec to use if no audio_file is provided 
            audio_bitrate: audio bitrate to use if no audio_file is provided
            ffmpeg_params: Any additional ffmpeg parameters you would like to pass, as a list
                           of terms, like ['-option1', 'value1', '-option2', 'value2']

        Use this method over moviepy's write_videofile to preserve the audio file's codec and bitrate.
        """
        audio = self.audio_file or True

        if not composed_music_video:
            composed_music_video = self.compose(dimensions=dimensions, aspect_ratio=aspect_ratio)
        self._write_video_clip_to_file(composed_music_video, output_path, audio=audio, codec=codec, crf=crf,
                                       audio_codec=audio_codec, audio_bitrate=audio_bitrate)

    def write_to_spec_file(self, filename):
        return

    def save_video_segments(self, directory: str, *, audio: Union[str, bool] = True,
                            dimensions: Opt[Tuple[int, int]] = None, aspect_ratio: Opt[float] = None,
                            codec: Opt[str] = None, crf: Opt[int] = None, audio_codec: Opt[str] = None,
                            audio_bitrate: Opt[str] = None, ffmpeg_params: Opt[List[str]] = None):
        """
        Saves video_segments to video files in the specified directory
        
        See write_to_video_file for descriptions of optional parameters
        """
        directory = os.path.join(directory, vc.SEGMENTS_DIRECTORY)
        util.recreate_dir(directory)
        self._write_video_segments_to_directory(self.video_segments, directory, audio=audio, dimensions=dimensions,
                                                aspect_ratio=aspect_ratio, codec=codec, crf=crf,
                                                audio_codec=audio_codec, audio_bitrate=audio_bitrate,
                                                ffmpeg_params=ffmpeg_params)

    def save_rejected_video_segments(self, directory: str, *, audio: Union[str, bool] = True,
                                     dimensions: Opt[Tuple[int, int]] = None, aspect_ratio: Opt[float] = None,
                                     codec: Opt[str] = None, crf: Opt[int] = None, audio_codec: Opt[str] = None,
                                     audio_bitrate: Opt[str] = None, ffmpeg_params: Opt[List[str]] = None):
        """
        Saves video_segment_rejects to video files in the specified directory
        
        See write_to_video_file for descriptions of optional parameters
        """
        directory = os.path.join(directory, vc.RS_DIRECTORY)
        util.recreate_dir(directory)
        self._write_video_segments_to_directory(self.rejected_video_segments, directory, audio=audio,
                                                dimensions=dimensions, aspect_ratio=aspect_ratio, codec=codec, crf=crf,
                                                audio_codec=audio_codec, audio_bitrate=audio_bitrate,
                                                ffmpeg_params=ffmpeg_params)

    def _write_video_segments_to_directory(self, video_segments: List[VideoSegment], directory: str, *,
                                           dimensions: Opt[Tuple[int, int]] = None, aspect_ratio: Opt[float] = None,
                                           **kwargs):
        """
        Writes a list of video segments to files in the specified directory
        """
        for index, segment in enumerate(video_segments):
            dimensions = self._determine_dimensions(dimensions, aspect_ratio)
            segment = segment.crop_scale(dimensions)

            output_path = os.path.join(directory, str(index) + vc.VIDEO_OUTPUT_EXTENSION)
            self._write_video_clip_to_file(segment, output_path, **kwargs)

    @staticmethod
    def _write_video_clip_to_file(video_clip: VideoClip, output_path: str, *, audio: Union[str, bool] = True,
                                  codec: Opt[str] = None, crf: Opt[int] = None, audio_codec: Opt[str] = None,
                                  audio_bitrate: Opt[str] = None, ffmpeg_params: Opt[List[str]] = None):
        """
        Writes a video clip to file in the specified directory
        """
        if codec is None:
            codec = vc.DEFAULT_VIDEO_CODEC
        if crf is None:
            crf = vc.DEFAULT_VIDEO_CRF
        if audio_codec is None:
            audio_codec = ac.DEFAULT_AUDIO_CODEC
        if audio_bitrate is None:
            audio_bitrate = ac.DEFAULT_AUDIO_BITRATE
        if ffmpeg_params is None:
            ffmpeg_params = []

        # Prepend crf to ffmpeg_params
        ffmpeg_params[:0] = ['-crf', crf]

        video_clip.write_videofile(output_path, audio=audio, codec=codec, audio_codec=audio_codec,
                                   audio_bitrate=audio_bitrate, ffmpeg_params=ffmpeg_params)

    def to_spec(self):
        return

    @classmethod
    def from_spec(cls, spec):
        return


