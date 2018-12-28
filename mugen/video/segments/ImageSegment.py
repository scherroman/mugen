from moviepy.video.VideoClip import ImageClip

from mugen import paths
from mugen.video.segments.Segment import Segment


class ImageSegment(Segment, ImageClip):
    """
    A segment with an image
    """
    file: str

    def __init__(self, file: str, duration: float = 1, **kwargs):
        """
        Parameters
        ----------
        file
            path to the image file.
            Supports any extension supported by ffmpeg.
        """
        super().__init__(file, duration=duration, **kwargs)

        self.file = file
        self.fps = Segment.DEFAULT_VIDEO_FPS

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}, duration: {self.duration}>"

    @property
    def name(self) -> str:
        return paths.filename_from_path(self.file)

    def trailing_buffer(self, duration) -> 'ImageSegment':
        return ImageSegment(self.file, duration)
