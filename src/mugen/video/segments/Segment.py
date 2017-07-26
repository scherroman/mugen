from abc import ABC, abstractmethod
from typing import List, Tuple
import copy

from moviepy.editor import VideoClip

import mugen.utility as util
import mugen.video.sizing as v_sizing
import mugen.video.effects as v_effects
from mugen.mixins.Filterable import Filterable
from mugen.video.effects import VideoEffectList
from mugen.video.constants import LIST_3D
from mugen.video.sizing import Dimensions


class Segment(Filterable, ABC):
    """
    A segment of content in a video.
    Simulates a wrapper for moviepy's VideoClip class.

    Attributes
    ----------
    effects
        A list of effects to apply to the segment when composed
    """
    effects: VideoEffectList

    DEFAULT_VIDEO_FPS = 24

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.effects = VideoEffectList()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>, duration: {self.duration}>"

    def __deepcopy__(self, memo):
        return self.copy()

    def copy(self) -> 'Segment':
        new_segment = super().copy()

        # Deepcopy effects
        new_segment.effects = copy.deepcopy(self.effects)

        return new_segment

    def ipython_display(self, *args, **kwargs):
        """
        Fixes inheritance naming issue with moviepy's ipython_display
        """
        seg_copy = self.copy()
        # Class should also always be set to VideoClip for expected video display
        seg_copy.__class__ = VideoClip().__class__
        return seg_copy.ipython_display(*args, **kwargs)

    @property
    def dimensions(self) -> Dimensions:
        return Dimensions(self.w, self.h)

    @property
    def aspect_ratio(self) -> float:
        return self.w / self.h

    @property
    def resolution(self) -> int:
        return self.w * self.h

    @property
    def duration_time_code(self) -> str:
        return util.seconds_to_time_code(self.duration)

    @property
    def first_frame(self) -> LIST_3D:
        return self.get_frame(t=0)

    @property
    def middle_frame(self) -> LIST_3D:
        return self.get_frame(t=self.duration / 2)

    @property
    def last_frame(self) -> LIST_3D:
        return self.get_frame(t=self.duration)

    @property
    def first_last_frames(self) -> List[LIST_3D]:
        return [self.first_frame, self.last_frame]

    @property
    def first_middle_last_frames(self) -> List[LIST_3D]:
        return [self.first_frame, self.middle_frame, self.last_frame]

    def crop_to_aspect_ratio(self, aspect_ratio: float) -> 'Segment':
        """
        Returns
        -------
        A new Segment, cropped as necessary to reach specified aspect ratio
        """
        segment = self.copy()

        if segment.aspect_ratio != aspect_ratio:
            # Crop video to match desired aspect ratio
            x1, y1, x2, y2 = v_sizing.crop_coordinates_for_aspect_ratio(segment.dimensions,
                                                                        aspect_ratio)
            segment = segment.crop(x1=x1, y1=y1, x2=x2, y2=y2)

        return segment

    def crop_scale(self, dimensions: Tuple[int, int]) -> 'Segment':
        """
        Returns
        -------
        A new Segment, cropped and/or scaled as necessary to reach specified dimensions
        """
        segment = self.copy()
        dimensions = Dimensions(*dimensions)

        if segment.aspect_ratio != dimensions.aspect_ratio:
            # Crop segment to match aspect ratio
            segment = segment.crop_to_aspect_ratio(dimensions.aspect_ratio)

        if segment.dimensions != dimensions:
            # Resize segment to reach final dimensions
            segment = segment.resize(dimensions)

        return segment

    def apply_effects(self) -> 'Segment':
        """
        Composes the segment, applying all effects

        Returns
        -------
        A new segment with all effects applied
        """
        segment = self.copy()

        for effect in self.effects:
            if isinstance(effect, v_effects.FadeIn):
                segment = segment.fadein(effect.duration, effect.rgb_color)
                if segment.audio:
                    segment.audio = segment.audio.audio_fadein(effect.duration)
            elif isinstance(effect, v_effects.FadeOut):
                segment = segment.fadeout(effect.duration, effect.rgb_color)
                if segment.audio:
                    segment.audio = segment.audio.audio_fadeout(effect.duration)

        return segment

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable name for the segment
        """
        pass

    @abstractmethod
    def trailing_buffer(self, duration) -> 'Segment':
        """
        Parameters
        ----------
        duration
            duration of the buffer

        Returns
        -------
        A new segment picking up where this one left off, for use in crossfades
        """
        pass
