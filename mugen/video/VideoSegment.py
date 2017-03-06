import random
from collections import OrderedDict

from moviepy.editor import VideoFileClip
from moviepy.decorators import convert_to_seconds

# Project modules
import mugen.constants as c

class VideoSegment(VideoFileClip, object):
    """
    A segment of video from a video file

    Attributes:
        source_video_file: The video file that the video segment comes from.
        source_video_start_time (float): Start time of the video segment in the source_video_file
        source_video_end_time (float): End time of the video segment in the source_video_file
        audio (bool): Enables or disables audio from the source_video_file
        video_traits (list of VideoTrait): Externally detected traits describing the video segment
    """

    @convert_to_seconds(['source_video_start_time', 'source_video_end_time'])
    def __init__(self, video_file, source_video_start_time=None, source_video_end_time=None, audio=False, 
                 video_traits=None, *args, **kwargs):
        """
        Args:
            video_file (str): A path to a video file. Can have any extension supported by ffmpeg.
            source_video_start_time (multiple): ~
            source_video_end_time (multiple): ~

            source_video_start_time, source_video_end_time accept the following formats:
            (SEC.MIL)
            (MIN, SEC.MIL)
            (HRS, MIN, SEC.MIL)
            'HRS:MIN:SEC.MIL'
        """
        super(VideoSegment, self).__init__(video_file, audio=audio, *args, **kwargs)
        self.source_video_file = video_file
        self.video_traits = video_traits if video_traits else []

        if source_video_start_time and source_video_end_time:
            self = self.subclip(source_video_start_time, source_video_end_time)
        else:
            self.source_video_start_time = 0
            self.source_video_end_time = self.duration

    @property
    def aspect_ratio(self):
        return self.w/float(self.h)

    def subclip(self, start_time, end_time):
        subclip = super(VideoSegment, self).subclip(start_time, end_time)
        subclip.source_video_start_time += start_time
        subclip.source_video_end_time -= (self.duration - end_time)

        return subclip

    def random_subclip(self, duration):
        start_time = random.uniform(0, self.duration - duration)
        end_time = start_time + duration

        return self.subclip(start_time, end_time)

    def resize(self, desired_dimensions):
        """
        Args:
            desired_dimensions (int, int)

        Returns (VideoSegment): New video segment, cropped and/or scaled as necessary to reach desired dimensions
        """
        resized_video_segment = None
        desired_aspect_ratio = desired_dimensions[0] / float(desired_dimensions[1])

        # Crop video segment if needed, to match aspect ratio
        if self.aspect_ratio > desired_aspect_ratio:
            # Crop sides
            cropped_width = int(desired_aspect_ratio * self.h)
            width_difference = self.w - cropped_width
            resized_video_segment = self.crop(x1=width_difference/2, x2=self.w - width_difference/2)
        elif self.aspect_ratio < desired_aspect_ratio:
            # Crop top & bottom
            cropped_height = int(self.w/desired_aspect_ratio)
            height_difference = self.h - cropped_height
            resized_video_segment = self.crop(y1=height_difference/2, y2=self.h - height_difference/2)

        # Resize video if needed, to match aspect ratio
        if self.size != desired_dimensions:
            # Video needs resize
            resized_video_segment = self.resize(desired_dimensions)
        else:
            # Video is already correct size
            resized_video_segment = self

        return resized_video_segment

    def to_spec(self):

    @classmethod
    def from_spec(cls):