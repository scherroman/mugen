import copy
from abc import ABC, abstractmethod
from typing import List

from moviepy.editor import VideoClip

from mugen.mixins.Filterable import Filterable
from mugen.mixins.Persistable import Persistable
from mugen.utilities import conversion
from mugen.video.constants import LIST_3D
from mugen.video.effects import VideoEffect
from mugen.video.sizing import Dimensions


class Segment(Filterable, Persistable, ABC):
    """
    A segment of content in a video.
    Simulates a wrapper for moviepy's VideoClip class.

    Attributes
    ----------
    effects
        A list of effects to apply to the segment when composed
    """

    effects: List[VideoEffect]

    DEFAULT_VIDEO_FPS = 24

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.effects = []

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>, duration: {self.duration}>"

    def __copy__(self):
        """
        Override copy to avoid causing conflicts with custom pickling
        """
        cls = self.__class__
        new_segment = cls.__new__(cls)
        new_segment.__dict__.update(self.__dict__)

        return new_segment

    def __deepcopy__(self, memo):
        return self.copy()

    def copy(self) -> "Segment":
        new_segment = super().copy()

        # Deepcopy effects
        new_segment.effects = copy.deepcopy(self.effects)

        return new_segment

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
        return conversion.seconds_to_time_code(self.duration)

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

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable name for the segment
        """
        pass

    @abstractmethod
    def trailing_buffer(self, duration) -> "Segment":
        """
        Parameters
        ----------
        duration
            duration of the buffer

        Returns
        -------
        A new segment spanning from the end of this segment until the specified duration
        """
        pass

    def ipython_display(self, *args, **kwargs):
        """
        Fixes inheritance naming issue with moviepy's ipython_display
        """
        seg_copy = self.copy()
        # Class should also always be set to VideoClip for expected video display
        seg_copy.__class__ = VideoClip().__class__
        return seg_copy.ipython_display(*args, **kwargs)
