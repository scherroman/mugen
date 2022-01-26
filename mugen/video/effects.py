from typing import List, Optional

from mugen.constants import Color
from mugen.lists import MugenList
from mugen.utilities import conversion
from mugen.utilities.conversion import convert_color_to_hex_code
from mugen.video.events import VideoEvent

ONE_SECOND = 1


class VideoEffect(VideoEvent):
    """
    A visual effect in a video
    """
    pass


class VideoEffectList(MugenList):
    """
    Wrapper for a list of Effects, providing convenience methods
    """

    def __init__(self, effects: Optional[List[VideoEffect]] = None):
        super().__init__(effects)

    def add_crossfade(self, duration: float = ONE_SECOND):
        """
        Adds a crossfade effect to the beginning of the video segment.

        Parameters
        ----------
        duration
            duration of the effect
        """
        self.append(CrossFade(duration))

    def add_fadein(self, duration: float = ONE_SECOND, color: str = Color.BLACK):
        """
        Adds a fade-in effect to the video segment.

        Parameters
        ----------
        duration
            duration of the effect

        color
            hex code of the color to fade in from, i.e. #000000 for black.
            OR the special inputs 'black' and 'white'.
        """
        self.append(FadeIn(duration, color))

    def add_fadeout(self, duration: float = ONE_SECOND, color: str = Color.BLACK):
        """
        Adds a fade-out effect to the video segment.

        Parameters
        ----------
        duration
            duration of the effect

        color
            hex code of the color to fade out to, i.e. #000000 for black.
            OR the special inputs 'black' and 'white'.
        """
        self.append(FadeOut(duration, color))


class Fade(VideoEffect):
    color: str

    @convert_color_to_hex_code(['color'])
    def __init__(self, color: str, **kwargs):
        super().__init__(**kwargs)
        self.color = color

    @property
    def rgb_color(self) -> List[int]:
        return conversion.hex_to_rgb(self.color)


class FadeIn(Fade):

    def __init__(self, duration: float, color: str, **kwargs):
        super().__init__(duration=duration, color=color, **kwargs)


class FadeOut(Fade):

    def __init__(self, duration: float, color: str, **kwargs):
        super().__init__(duration=duration, color=color, **kwargs)


class CrossFade(VideoEffect):

    def __init__(self, duration: float, **kwargs):
        super().__init__(duration=duration, **kwargs)
