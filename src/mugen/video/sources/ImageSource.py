from mugen.video.segments.ImageSegment import ImageSegment
from mugen.video.sources.Source import Source


class ImageSource(Source):
    """
    An image source for sampling image segments
    """

    def __init__(self, file: str, **kwargs):
        super().__init__(**kwargs)
        self.segment = ImageSegment(file)

    @property
    def file(self):
        return self.segment.file

    @property
    def name(self):
        return self.segment.name

    def sample(self, duration: float) -> ImageSegment:
        """
        Samples an ImageSegment with the specified duration

        Parameters
        ----------
        duration
            duration of the image to sample
        """
        return self.segment.set_duration(duration)
