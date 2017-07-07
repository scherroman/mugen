from typing import List

from mugen import utility as util
from mugen.video.events import VideoEvent

FADE_DURATION = 1
FADE_COLOR = '#000000'


class VideoEffect(VideoEvent):
    """
    A visual effect in a video
    """
    pass


class Fade(VideoEffect):
    color: str

    def __init__(self, color: str, **kwargs):
        super().__init__(**kwargs)
        self.color = color

    @property
    def rgb_color(self) -> List[int]:
        return util.hex_to_rgb(self.color)


class FadeIn(Fade):

    def __init__(self, duration: float = FADE_DURATION, color: str = FADE_COLOR, **kwargs):
        super().__init__(duration=duration, color=color, **kwargs)


class FadeOut(Fade):

    def __init__(self, duration: float = FADE_DURATION, color: str = FADE_COLOR, **kwargs):
        super().__init__(duration=duration, color=color, **kwargs)


class CrossFade(VideoEffect):

    def __init__(self, duration: float = FADE_DURATION, **kwargs):
        super().__init__(duration=duration, **kwargs)
