from mugen.video.segments.ColorSegment import ColorSegment
from mugen.video.sources.Source import Source


class ColorSource(Source):
    """
    An color source for sampling color segments
    """

    def __init__(self, color: str, **kwargs):
        """
        Parameters
        ----------
        color
            hex code of the color, i.e. #000000 for black.
            OR the special inputs 'black' and 'white'.
        """
        super().__init__(**kwargs)
        self.segment = ColorSegment(color)

    @property
    def color(self):
        return self.segment.color

    @property
    def name(self):
        return self.segment.name

    def sample(self, duration: float) -> ColorSegment:
        """
        Samples an ColorSegment with the specified duration

        Parameters
        ----------
        duration
            duration of the color to sample
        """
        return self.segment.set_duration(duration)
