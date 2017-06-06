import json
import random
from typing import Optional as Opt, List, Tuple, Union, Any

from moviepy.editor import VideoFileClip

import mugen.utility as util
import mugen.video.sizing as v_sizing
from mugen import paths
from mugen.utility import convert_time_to_seconds
from mugen.video.sizing import Dimensions
from mugen.constants import TIME_FORMAT
from mugen.video.constants import LIST_3D
from mugen.mixins.Taggable import Taggable
from mugen.mixins.Filterable import Filterable
from mugen.mixins.Weightable import Weightable, WeightableList

DEFAULT_VIDEO_FPS = 24


class VideoSegment(Taggable, Weightable, Filterable, VideoFileClip):
    """
    A segment of video from a video file

    Attributes
    ----------
    source_start_time
        Start time of the video segment in the video file (seconds)
    """
    source_start_time: float

    def __init__(self, filename: str, *, audio: bool = True, **kwargs):
        """
        Parameters
        ----------
        filename
            The name of the video file.
            Supports any extension supported by ffmpeg
            
        audio
            Enables or disables audio
        """
        super().__init__(**kwargs)
        VideoFileClip.__init__(self, filename, audio=audio, **kwargs)

        self.source_start_time = 0

        # Parent VideFileClip will not always be able to properly read an fps value
        if not self.fps:
            self.fps = DEFAULT_VIDEO_FPS

    def __repr__(self):
        filename = paths.filename_from_path(self.video_file)
        return f"<VideoSegment, file: {filename}, source_start_time:{self.source_start_time}, " \
               f"duration: {self.duration}>"

    """ PROPERTIES """

    @property
    def video_file(self):
        return self.filename

    @property
    def source_end_time(self):
        return self.source_start_time + self.duration

    @property
    def duration_time_code(self):
        return util.seconds_to_time_code(self.duration)

    @property
    def dimensions(self) -> Dimensions:
        return Dimensions(self.w, self.h)

    @property
    def aspect_ratio(self) -> float:
        return self.w / self.h

    @property
    def resolution(self) -> int:
        return self.w * self.h

    @property
    def first_frame(self) -> LIST_3D:
        return self.get_frame(t=0)

    @property
    def middle_frame(self) -> LIST_3D:
        return self.get_frame(t=self.duration / 2)

    @property
    def last_frame(self) -> LIST_3D:
        return self.get_frame(t=self.duration)

    @property
    def first_last_frames(self) -> List[LIST_3D]:
        return [self.first_frame, self.last_frame]

    @property
    def first_middle_last_frames(self) -> List[LIST_3D]:
        return [self.first_frame, self.middle_frame, self.last_frame]

    """ METHODS """

    @convert_time_to_seconds(['start_time', 'duration'])
    def subclip(self, start_time: TIME_FORMAT = 0, duration: TIME_FORMAT = None) -> 'VideoSegment':
        """
        Parameters
        ----------
        start_time
            Start time of the video segment in the source video file
            
        duration
            Duration of the subclip

        Returns
        -------
        A subclip of the original video file, starting at 'start_time' and lasting for 'duration'
        """
        subclip = super().subclip(start_time, start_time + duration)

        if start_time < 0:
            # Set relative to end
            start_time = self.duration + start_time

        subclip.source_start_time += start_time

        return subclip

    @convert_time_to_seconds(['duration'])
    def random_subclip(self, duration: TIME_FORMAT) -> 'VideoSegment':
        start_time = random.uniform(0, self.duration - duration)

        return self.subclip(start_time, duration)

    def crop_scale(self, desired_dimensions: Tuple[int, int]) -> 'VideoSegment':
        """
        Returns
        -------
        A new VideoSegment, cropped and/or scaled as necessary to reach desired dimensions
        """
        desired_dimensions = Dimensions(*desired_dimensions)
        segment = self.copy()

        if segment.aspect_ratio != desired_dimensions.aspect_ratio:
            # Crop video to match desired aspect ratio
            x1, y1, x2, y2 = v_sizing.crop_coordinates_for_aspect_ratio(segment.dimensions,
                                                                        desired_dimensions.aspect_ratio)
            segment = segment.crop(x1=x1, y1=y1, x2=x2, y2=y2)

        if segment.dimensions != desired_dimensions:
            # Resize video to match aspect ratio
            segment = segment.resize(desired_dimensions)

        return segment

    def overlaps_segment(self, segment: 'VideoSegment') -> bool:
        if not self.filename == segment.filename:
            return False

        return util.ranges_overlap(self.source_start_time, self.source_end_time, segment.source_start_time,
                                   segment.source_end_time)

    def to_spec(self) -> str:
        spec = {'source_video': self.filename,
                'source_start_time': self.source_start_time,
                'duration': self.duration}

        return json.dumps(spec)

    @classmethod
    def from_spec(cls, spec: dict) -> 'VideoSegment':
        video_segment = cls(spec['source_video'])
        video_segment = video_segment.subclip(spec['source_start_time'], spec['duration'])

        return video_segment

    @staticmethod
    def video_segments_from_irregular_source_list(video_sources: List[Union[str, List[str]]]) -> List['VideoSegment']:
        """
        Converts an arbitrarily nested irregular list of video sources to VideoSegments
        """
        video_segments = []

        for video_source in video_sources:
            if type(video_source) is list:
                video_segments.append(VideoSegment.video_segments_from_irregular_source_list(video_source))
            else:
                video_segments.append(VideoSegment(video_source))

        return video_segments


class VideoSegmentList(WeightableList):
    """
    A list of Video Segments with extended functionality
    """

    def __init__(self, video_segments: Opt[List[Union[VideoSegment, List[Any]]]] = None,
                 weights: Opt[List[float]] = None):
        """
        Parameters
        ----------
        video_segments
            An arbitrarily nested irregular list of VideoSegments and lists of VideoSegments.
            VideoSegments will be flattened.
            e.g. [S1, S2, [S3, S4]] -> [S1, S2, S3, S4]

        weights
            Weights to distribute across the video_segments
        """
        if video_segments is None:
            video_segments = []

        super().__init__(video_segments, weights)

    def to_spec(self) -> List[dict]:
        spec = [segment.to_spec() for segment in self]

        return json.dumps(spec)
