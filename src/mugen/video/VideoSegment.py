import random
from typing import Optional as Opt, List, Tuple

from moviepy.editor import VideoFileClip

import mugen.video.constants as vc
import mugen.video.utility as v_util
import mugen.video.sizing as v_sizing
from mugen.utility import convert_time_to_seconds
from mugen.video.sizing import Dimensions
from mugen.constants import TIME_FORMAT
from mugen.video.constants import LIST_3D
from mugen.mixins.Taggable import Taggable
from mugen.mixins.Filterable import Filterable
from mugen.mixins.Weightable import Weightable


class VideoSegment(Taggable, Weightable, Filterable, VideoFileClip):
    """
    A segment of video from a video file

    Attributes:
        source_start_time: Start time of the video segment in the source video (sec.mil)
        source_end_time: End time of the video segment in the source video (sec.mil)
    """
    source_start_time: float
    source_end_time: float

    def __init__(self, filename: str, audio: bool = False, *args, **kwargs):
        """
        Args:
            source_video_file (str): A path to a video file. Can have any extension supported by ffmpeg.
            audio (bool): Enables or disables audio from the source video file
        """
        super().__init__(filename, audio=audio, *args, **kwargs)

        self.source_start_time = 0
        self.source_end_time = self.duration
        if not self.fps:
            self.fps = vc.DEFAULT_VIDEO_FPS

    """ PROPERTIES """

    @property
    def duration_time_code(self):
        return v_util.seconds_to_time_code(self.duration)

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

    @convert_time_to_seconds(['start_time', 'end_time'])
    def subclip(self, start_time: TIME_FORMAT = 0, end_time: Opt[TIME_FORMAT] = None) -> 'VideoSegment':
        """
        Args:
            start_time: Start time of the video segment in the source video file
            end_time: End time of the video segment in the source video file

        Returns: A subclip of the original video file, starting and ending at the specified times
        """
        subclip = super().subclip(start_time, end_time)

        if start_time < 0:
            start_time = self.duration + start_time
        if not end_time:
            end_time = self.duration
        elif end_time < 0:
            end_time = self.duration + end_time

        subclip.source_start_time += start_time
        subclip.source_end_time -= (self.duration - end_time)

        return subclip

    @convert_time_to_seconds(['duration'])
    def random_subclip(self, duration: TIME_FORMAT) -> 'VideoSegment':
        start_time = random.uniform(0, self.duration - duration)
        end_time = start_time + duration

        return self.subclip(start_time, end_time)

    def crop_scale(self, desired_dimensions: Tuple[int, int]) -> 'VideoSegment':
        """
        Returns: A new VideoSegment, cropped and/or scaled as necessary to reach desired dimensions
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

        return v_util.ranges_overlap(self.source_start_time, self.source_end_time, segment.source_start_time,
                                     segment.source_end_time)

    def to_spec(self):
        return


    @classmethod
    def from_spec(cls, spec):
        return
