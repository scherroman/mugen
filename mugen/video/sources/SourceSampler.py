from typing import List, Union

from numpy.random import choice

from mugen.video.filters import VideoFilter
from mugen.video.segments import Segment
from mugen.video.sources.Source import SourceList


class SourceSampler:
    """
    A set of content sources for sampling video segments
    """

    sources: SourceList

    def __init__(self, sources: Union[SourceList, list]):
        """
        video_segments

        Parameters
        ----------
        sources
            An arbitrarily nested list of sources. Sources will be flattened internally.
            e.g. [S1, S2, [S3, S4]] -> [S1, S2, S3, S4]
        """
        if not isinstance(sources, SourceList):
            sources = SourceList(sources)

        self.sources = sources.flatten()

    def sample(self, duration: float) -> Segment:
        """
        Randomly samples a segment with the specified duration

        Parameters
        ----------
        duration
            duration of the sample

        Returns
        -------
        A randomly sampled segment with the specified duration
        """
        selected_source = choice(self.sources, p=self.sources.normalized_weights)
        sample = selected_source.sample(duration)

        return sample

    def sample_with_filters(self, duration: float, filters: List[VideoFilter]):
        """
        Randomly samples a segment with the specified duration which passes the specified filters

        Parameters
        ----------
        duration
            duration of the sample
        filters
            duration of the sample

        Returns
        -------
        A tuple of a randomly sampled segment with the specified duration, and any rejected segments
        """
        video_segment = None
        rejected_video_segments = []
        while not video_segment:
            sampled_segment = self.sample(duration)
            sampled_segment.apply_filters(filters)
            if not sampled_segment.failed_filters:
                video_segment = sampled_segment
            else:
                rejected_video_segments.append(sampled_segment)

        return video_segment, rejected_video_segments
