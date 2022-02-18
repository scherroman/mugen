from typing import Union

from numpy.random import choice

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
