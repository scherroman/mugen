from abc import ABC, abstractmethod
from typing import List

from mugen.constants import Color
from mugen.utilities import conversion
from mugen.utilities.conversion import convert_color_to_hex_code
from mugen.video.events import VideoEvent

ONE_SECOND = 1


class VideoEffect(VideoEvent, ABC):
    """
    A visual effect in a video
    """

    pass

    @abstractmethod
    def apply(self):
        """
        Applies the effect to a segment
        """
        pass


class Fade(VideoEffect):
    color: str

    @convert_color_to_hex_code(["color"])
    def __init__(self, color: str, **kwargs):
        super().__init__(**kwargs)
        self.color = color

    @property
    def rgb_color(self) -> List[int]:
        return conversion.hex_to_rgb(self.color)


class FadeIn(Fade):
    """
    Adds a fade-in effect to the video segment
    """

    def __init__(
        self, duration: float = ONE_SECOND, color: str = Color.BLACK, **kwargs
    ):
        """
        Parameters
        ----------
        duration
            duration of the effect

        color
            hex code of the color to fade in from, i.e. #000000 for black.
            OR the special inputs 'black' and 'white'.
        """
        super().__init__(duration=duration, color=color, **kwargs)

    def apply(self, segment):
        segment = segment.fadein(self.duration, self.rgb_color)
        if segment.audio:
            segment.audio = segment.audio.audio_fadein(self.duration)

        return segment


class FadeOut(Fade):
    """
    Adds a fade-out effect to the video segment
    """

    def __init__(
        self, duration: float = ONE_SECOND, color: str = Color.BLACK, **kwargs
    ):
        """
        Parameters
        ----------
        duration
            duration of the effect

        color
            hex code of the color to fade out to, i.e. #000000 for black.
            OR the special inputs 'black' and 'white'.
        """
        super().__init__(duration=duration, color=color, **kwargs)

    def apply(self, segment):
        segment = segment.fadeout(self.duration, self.rgb_color)
        if segment.audio:
            segment.audio = segment.audio.audio_fadeout(self.duration)

        return segment


class Crossfade(VideoEffect):
    """
    Adds a crossfade effect to the beginning of the video segment
    """

    def __init__(self, duration: float = ONE_SECOND, **kwargs):
        """
        Parameters
        ----------
        duration
            duration of the effect
        """
        super().__init__(duration=duration, **kwargs)

    def apply(self, segment, previous_segment):
        segment = segment.set_start(previous_segment.end - self.duration)
        segment = segment.crossfadein(self.duration)
        if segment.audio:
            segment = segment.set_audio(segment.audio.audio_fadein(self.duration))

        return segment

    def buffer(self, segment):
        buffer = segment.trailing_buffer(self.duration)
        if buffer.audio:
            buffer = buffer.set_audio(buffer.audio.audio_fadeout(self.duration))

        return buffer
