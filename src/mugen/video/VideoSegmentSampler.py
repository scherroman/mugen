from numpy.random import choice

from mugen.utility import convert_time_to_seconds
from mugen.constants import TIME_FORMAT
from mugen.video.VideoSegment import VideoSegment, VideoSegmentList


class VideoSegmentSampler:
    """
    A set of video segments for sampling other video segments from
    """
    video_sources: VideoSegmentList

    def __init__(self, video_segments: VideoSegmentList):
        self.video_sources = video_segments

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
        sample_source = choice(self.video_sources, p=self.video_sources.normalized_weights)
        sample = sample_source.random_subclip(duration)

        return sample
