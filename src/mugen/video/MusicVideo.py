from typing import List, Optional as Opt, Tuple

from moviepy.editor import AudioFileClip, VideoClip

import mugen.video.constants as vc
import mugen.paths as paths
import mugen.utility as util
import mugen.video.sizing as v_sizing
from mugen.utility import sanitize_directory_name, ensure_json_serializable
from mugen.mixins.Taggable import Taggable
from mugen.mixins.TraitFilterable import TraitFilter
from mugen.video.VideoSegment import VideoSegment
from mugen.video.sizing import Dimensions


class MusicVideo(Taggable):
    """
    A music video composed of video segments and audio.

    Attributes:
        source_videos: Videos used to sample video segments from
        music_video_segments: Video segments composing the music video
        audio: Audio for the music video
        rejected_music_video_segments: Video segments rejected from the music video
        _dimensions: Width and height for the music video
        _aspect_ratio: Aspect ratio for the music video (Overruled by _dimensions)
        _fps: frames per second for the music video
        codec: video codec to use when writing the music video to file
        crf: constant rate factor (quality) for the music video (0 - 51)
        meta: Json serializable dictionary with metadata describing the music video
    """
    music_video_segments: List[VideoSegment]
    audio: AudioFileClip

    _dimensions: Opt[Dimensions] = None
    _aspect_ratio: Opt[float] = None
    _fps: int = None
    codec: str = vc.DEFAULT_VIDEO_CODEC
    crf: int = vc.DEFAULT_VIDEO_CRF

    source_videos: List[VideoSegment]
    rejected_music_video_segments: List[VideoSegment]
    video_segment_trait_filters: List[TraitFilter]
    meta: dict

    @ensure_json_serializable('meta')
    def __init__(self, music_video_segments: List[VideoSegment], audio_file: str,
                 dimensions: Opt[Tuple[int, int]] = None, aspect_ratio: Opt[float] = None, fps: Opt[int] = None,
                 codec: Opt[str] = None, crf: Opt[int] = None, source_videos: Opt[List[VideoSegment]] = None,
                 rejected_music_video_segments: Opt[List[VideoSegment]] = None,
                 video_segment_trait_filters: Opt[List[TraitFilter]] = None, meta: Opt[dict] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Required Parameters
        self.music_video_segments = music_video_segments
        self.audio = AudioFileClip(audio_file)

        # Optional Parameters
        if dimensions:
            self._dimensions = Dimensions(*dimensions)
        if aspect_ratio:
            self._aspect_ratio = aspect_ratio
        if fps:
            self._fps = fps
        if codec:
            self.codec = codec
        if crf is not None:
            self.crf = crf
        self.source_videos = source_videos or []
        self.rejected_music_video_segments = rejected_music_video_segments or []
        self.video_segment_trait_filters = video_segment_trait_filters or []
        self.meta = meta or {}

    """ PROPERTIES """

    @property
    def dimensions(self) -> Opt[Dimensions]:
        """
        Returns: _dimensions if set, or calculates them from dimensions of video segments and _aspect_ratio
        """
        if self._dimensions:
            dimensions = self._dimensions
        elif self._aspect_ratio:
            dimensions = v_sizing.largest_dimensions_for_aspect_ratio(
                            [segment.dimensions for segment in self.music_video_segments],
                            self._aspect_ratio, default=None)
        else:
            dimensions = v_sizing.largest_width_and_height_for_dimensions(
                            [segment.dimensions for segment in self.music_video_segments], default=None)

        return dimensions

    @dimensions.setter
    def dimensions(self, value: Tuple[int, int]):
        self._dimensions = Dimensions(*value)

    @property
    def aspect_ratio(self) -> float:
        dimensions = self.dimensions
        return dimensions.aspect_ratio if dimensions else self._aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, value: float):
        self._aspect_ratio = value

    @property
    def fps(self) -> int:
        return self._fps if self._fps else max([video_segment.fps for video_segment in self.music_video_segments])

    @fps.setter
    def fps(self, value: int):
        self._fps = value

    @property
    def duration(self) -> float:
        """
        Returns: Duration of the music video, calculated from durations of video segments
        """
        return sum([segment.duration for segment in self.music_video_segments])

    @property
    def cut_locations(self) -> List[float]:
        """
        (list of float): Locations in the music video where a change between video segments occurs (sec)
        """
        cut_locations = []
        running_duration = 0
        for index, segment in enumerate(self.music_video_segments):
            if index != len(self.music_video_segments) - 1:
                cut_locations.append(segment.duration + running_duration)
                running_duration += segment.duration

        return cut_locations

    @property
    def cut_intervals(self) -> List[float]:
        """
        (list of float): Intervals between each cut location (sec)
        """
        cut_intervals = []
        for segment in self.music_video_segments:
            cut_intervals.append(segment.duration)

        return cut_intervals

    """ METHODS """

    def compose(self) -> VideoClip:
        """
        Returns a composed VideoClip of the music video
        """
        # segments = resize videoSegments
        # concatenate_videoclips
        # Return VideoClip


    def write_to_video_file(self, filename, composed_music_video: Opt[VideoClip] = None, *args, **kwargs):
        """
        Args:
            filename: Name for the video file
            composed_music_video: A composed music video to

        """
        if not composed_music_video:
            # compose
        composed_music_video.write_videofile()
        # if mp3, find audio bitrate via ffprobe
        # add_auxiliary_tracks


    def write_to_spec_file(self, filename):


    def _write_video_segment_files_to_directory(self, video_segments, directory):
        """
        Writes a list of video segments to video files in the specified directory

        Args:
            video_segments (list of VideoSegment): Video Segments to write to video files
            directory (str): Directory to save the video files in
        """
        for index, segment in enumerate(video_segments):
            segment.write_videofile(paths.video_file_output_path(str(index), directory), fps=self.fps,
                                    codec=self.codec, ffmpeg_params=['-crf', self.crf])


    @sanitize_directory_name('directory')
    def save_video_segments(self, directory=paths.OUTPUT_PATH_BASE):
        """
        Saves video_segments to video files in the specified directory

        Args:
            directory (str): Directory to save the video files in
        """
        segments_dir = paths.segments_dir(self.name, directory)
        util.ensure_dir(paths.segments_basedir(directory))
        util.recreate_dir(segments_dir)
        self._write_video_segment_files_to_directory(self.music_video_segments, segments_dir)


    @sanitize_directory_name('directory')
    def save_video_segment_rejects(self, directory=paths.OUTPUT_PATH_BASE):
        """
        Saves video_segment_rejects to video files in the specified directory

        Args:
            directory (str): Directory to save the video files in
        """
        util.ensure_dir(paths.sr_dir(self.name, directory))
        # for VideoTraitFilter, ensure sr_trait_dir
        # self._write_video_segment_files_to_directory(self.video_segment_rejects, paths.dir_for_sr_trait)


    def to_spec(self):


    @classmethod
    def from_spec(cls, spec):


