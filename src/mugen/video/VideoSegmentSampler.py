import math
from typing import List

from numpy.random import choice
from moviepy.decorators import convert_to_seconds

from mugen.video.constants import TIME_FORMAT
from mugen.video.VideoSegment import VideoSegment
from mugen.mixins.Weightable import Weightable


class VideoSegmentSampler:
    """
    A set of video segments for sampling other video segments from
    """
    video_segments: List[VideoSegment] = []

    def __init__(self, video_segments: List[VideoSegment]):
        self.video_segments = video_segments

    @property
    def weights(self):
        return [video_segment.weight for video_segment in self.video_segments]

    @convert_to_seconds(['duration'])
    def sample(self, duration: TIME_FORMAT) -> VideoSegment:
        """
        Args:
            duration: duration of the sample

        Returns: Randomly sampled video segment with the specified duration
        """
        weights = Weightable.normalized_weights(self.weights)
        sample_source = choice(self.video_segments, p=weights)
        sample = sample_source.random_subclip(duration)

        return sample
