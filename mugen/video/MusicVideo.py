from typing import Optional

# Project modules
import mugen.constants as c
import mugen.paths as paths
from mugen.utility import sanitize_directory_name
import mugen.video.sizing as v_sizing
from mugen.video.sizing import Dimensions

class MusicVideo:
    """
    A music video composed of video segments and audio.

    Attributes:
        source_videos (VideoSet): Videos used to sample video segments from
        music_video_segments (list of VideoSegment): Video segments composing the music video
        video_segment_rejects (list of VideoSegment): Video segments rejected from the music video
        audio (AudioFileClip): Audio for the music video
        _dimensions (Dimensions): Width and height for the music video
        _aspect_ratio (float): Aspect ratio for the music video (Overruled if _dimensions is set)
        crf (int): crf quality value for the music video
        cutting_method (dict): Json Serializable dict with metadata describing method used to determine cut locations
    """

    def __init__(self, source_videos, music_video_segments, audio, music_video_segment_rejects=None,
                 dimensions: (int, int) = None, aspect_ratio: Optional[float] = None, crf=c.DEFAULT_VIDEO_CRF,
                 fps=c.DEFAULT_VIDEO_FPS, codec=c.DEFAULT_VIDEO_CODEC, cutting_method=None):
        # Required Parameters
        self.source_videos = source_videos if source_videos else []
        self.music_video_segments = music_video_segments if music_video_segments else []
        self.audio = audio

        # Optional Parameters
        self.crf = crf
        self.fps = fps
        self.codec = codec
        self.video_segment_rejects = music_video_segment_rejects if music_video_segment_rejects else []
        self._dimensions = Dimensions(*dimensions)
        self._aspect_ratio = aspect_ratio
        self.cutting_method = cutting_method

    @property
    def duration(self) -> float:
        """
        Returns: Duration of the music video, calculated from durations of video segments
        """
        return sum([segment.duration for segment in self.music_video_segments])

    @property
    def dimensions(self) -> Optional[Dimensions]:
        """
        Returns: _dimensions if set, or calculated from dimensions of video segments and aspect_ratio
        """
        if self._dimensions:
            return self._dimensions
        elif not self.music_video_segments:
            return None
        else:
            return v_sizing.largest_dimensions_for_aspect_ratio([segment.dimensions for segment in self.music_video_segments],
                                                                self._aspect_ratio)

    @property
    def aspect_ratio(self) -> float:
        dimensions = self.dimensions
        return dimensions[0]/dimensions[1] if dimensions else None

    @property
    def cut_locations(self):
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
    def cut_intervals(self):
        """
        (list of float): Intervals between each cut location (sec)
        """
        cut_intervals = []
        for segment in self.music_video_segments:
            cut_intervals.append(segment.duration)

        return cut_intervals

    def compose(self):
        """
        Returns (VideoClip): A composed VideoClip of the music video
        """
        # resize copy of videoSegments (resizing is destructive)
        # concatenate_videoclips
        # Return VideoClip

    def write_to_video_file(self, filename, *args, **kwargs):
        # compose
        # write_videofile()
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


