from abc import ABC, abstractmethod
from typing import Optional as Opt, List, Union

from numpy.random import choice

from mugen.mixins.Taggable import Taggable
from mugen.mixins.Weightable import Weightable, WeightableList
from mugen.video.segments import Segment


class Source(Taggable, Weightable, ABC):
    """
    A content source for sampling segments of content
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable name for the source
        """
        pass

    @abstractmethod
    def sample(self, duration: float) -> Segment:
        pass


class SourceList(WeightableList):
    """
    A list of sources
    """

    def __init__(self, sources: Opt[List[Union[Source, 'SourceList']]] = None, *, weights: List[float] = None,
                 **kwargs):
        """
        Parameters
        ----------
        sources
            A list of Sources

        weights
            weights to apply to top-most level sources
        """
        super().__init__(sources, **kwargs)

        if weights:
            for source, weight in zip(sources, weights):
                source.weight = weight

    def __repr__(self):
        source_reprs = []
        for source in self:
            if isinstance(source, SourceList):
                source_repr = source.list_repr()
            else:
                source_repr = repr(source)

            source_reprs.append(source_repr)

        return f"<{super().pretty_repr(source_reprs)}>"

    def list_repr(self):
        """
        Repr for use in lists
        """
        return f"<{self.__class__.__name__} ({len(self)}): weight: {self.weight}>"

    def weight_stats(self) -> str:
        """
        Returns
        -------
        A string describing the weights for the sources
        """
        flattened_sources = self.flatten()

        string = ""
        for index, (source, weight) in enumerate(zip(flattened_sources, flattened_sources.weight_percentages)):
            string += f"{source.name}: {weight:.2f}%"
            if index != len(flattened_sources) - 1:
                string += ', \n'

        return string
