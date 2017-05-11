from typing import List

from numpy.random import choice

from mugen.utility import convert_time_to_seconds
from mugen.constants import TIME_FORMAT
from mugen.video.VideoSegment import VideoSegment
from mugen.mixins.Weightable import Weightable


class VideoSegmentSampler:
    """
    A set of video segments for sampling other video segments from
    """
    video_sources: List[VideoSegment] = []

    def __init__(self, video_segments: List[VideoSegment]):
        self.video_sources = video_segments

    @property
    def weights(self):
        return [video_segment.weight for video_segment in self.video_sources]

    @convert_time_to_seconds('duration')
    def sample(self, duration: TIME_FORMAT) -> VideoSegment:
        """
        Randomly samples a video segment with the specified duration
        
        Parameters
        ----------
        duration
            duration of the sample

        Returns
        -------
        A randomly sampled video segment with the specified duration
        """
        weights = Weightable.normalized_weights(self.weights)
        sample_source = choice(self.video_sources, p=weights)
        sample = sample_source.random_subclip(duration)

        return sample
