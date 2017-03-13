import random
from typing import TypeVar

from moviepy.editor import VideoFileClip
from moviepy.decorators import convert_to_seconds

# Project modules
from mugen.mixins import TraitFilterable
from mugen.video.sizing import Dimensions

class VideoSegment(TraitFilterable, VideoFileClip):
    """
    A segment of video from a video file

    Attributes:
        source_video_start_time (float): Start time of the video segment in the source video file (sec.mil)
        source_video_end_time (float): End time of the video segment in the source video file (sec.mil)
    """

    """
    TIME_FORMAT accepts the following formats:

    SEC.MIL or 'SEC.MIL'
    (MIN, SEC.MIL) or 'MIN:SEC.MIL'
    (HRS, MIN, SEC.MIL) or 'HRS:MIN:SEC.MIL'
    """
    TIME_FORMAT = TypeVar(float, (int, float), (int, int, float), str)

    def __init__(self, source_video_file: str, audio: bool = False, *args, **kwargs):
        """
        Args:
            source_video_file (str): A path to a video file. Can have any extension supported by ffmpeg.
            audio (bool): Enables or disables audio from the source video file
        """
        super().__init__(source_video_file, audio=audio, *args, **kwargs)

        self.source_video_start_time = 0
        self.source_video_end_time = self.duration

    @property
    def source_video_file(self) -> str:
        return self.filename

    @property
    def dimensions(self) -> Dimensions:
        return Dimensions(self.w, self.h)

    @property
    def aspect_ratio(self) -> float:
        return self.w/self.h

    @convert_to_seconds(['start_time', 'end_time'])
    def subclip(self, start_time: TIME_FORMAT = 0, end_time: TIME_FORMAT = None) -> 'VideoSegment':
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

        subclip.source_video_start_time += start_time
        subclip.source_video_end_time -= (self.duration - end_time)

        return subclip

    @convert_to_seconds(['duration'])
    def random_subclip(self, duration: TIME_FORMAT) -> 'VideoSegment':
        start_time = random.uniform(0, self.duration - duration)
        end_time = start_time + duration

        return self.subclip(start_time, end_time)

    def crop_scale(self, desired_dimensions: (int, int)) -> 'VideoSegment':
        """
        Returns: New video segment, cropped and/or scaled as necessary to reach desired dimensions
        """
        desired_dimensions = Dimensions(*desired_dimensions)
        resized_video_segment = None

        # Crop video segment if necessary to match aspect ratio
        if self.aspect_ratio > desired_dimensions.aspect_ratio:
            # Crop sides
            cropped_width = int(desired_dimensions.aspect_ratio * self.h)
            width_difference = self.w - cropped_width
            resized_video_segment = self.crop(x1=width_difference/2, x2=self.w - width_difference/2)
        elif self.aspect_ratio < desired_dimensions.aspect_ratio:
            # Crop top & bottom
            cropped_height = int(self.w/desired_dimensions.aspect_ratio)
            height_difference = self.h - cropped_height
            resized_video_segment = self.crop(y1=height_difference/2, y2=self.h - height_difference/2)

        # Resize video if needed, to match aspect ratio
        if self.dimensions != desired_dimensions:
            # Video needs resize
            resized_video_segment = self.resize(desired_dimensions)
        else:
            # Video is already correct size
            resized_video_segment = self

        return resized_video_segment