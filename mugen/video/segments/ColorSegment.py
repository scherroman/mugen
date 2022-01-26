from typing import Tuple, Optional

from moviepy.video.VideoClip import ColorClip

from mugen.utilities import conversion
from mugen.utilities.conversion import convert_color_to_hex_code
from mugen.video.segments.Segment import Segment


class ColorSegment(Segment, ColorClip):
    """
    A segment with a color
    """
    color: str

    @convert_color_to_hex_code(['color'])
    def __init__(self, color: str, duration: float = 1, size: Optional[Tuple[int, int]] = (300, 300), **kwargs):
        """
        Parameters
        ----------
        color
            hex code of the color, i.e. #000000 for black.
            OR the special inputs 'black' and 'white'.
        """
        super().__init__(size, conversion.hex_to_rgb(color), duration=duration, **kwargs)

        self.color = color
        self.fps = Segment.DEFAULT_VIDEO_FPS

    @property
    def name(self):
        return self.color

    def trailing_buffer(self, duration) -> 'ColorSegment':
        return ColorSegment(self.color, duration, self.size)
