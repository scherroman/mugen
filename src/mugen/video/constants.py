from enum import Enum
from typing import TypeVar, Union, Tuple

import numpy as np

DEFAULT_MUSIC_VIDEO_NAME = 'music_video'

DEFAULT_VIDEO_CRF = 18
DEFAULT_VIDEO_FPS = 24
DEFAULT_VIDEO_CODEC = 'libx264'

LIST_3D = np.ndarray

"""
TIME_FORMAT accepts the following formats:

SEC.MIL or 'SEC.MIL'
(MIN, SEC.MIL) or 'MIN:SEC.MIL'
(HRS, MIN, SEC.MIL) or 'HRS:MIN:SEC.MIL'
"""
TIME_FORMAT = TypeVar(Union[float, Tuple[int, float], Tuple[int, int, float], str])


class VideoTrait(str, Enum):
    IS_REPEAT = 'is_repeat'
    HAS_TEXT = 'has_text'
    HAS_SCENE_CHANGE = 'has_scene_change'
    HAS_SOLID_COLOR = 'has_solid_color'


class SubtitlesTrack(str, Enum):
    SEGMENT_NUMBERS = 'segment_numbers'
    SEGMENT_DURATIONS = 'segment_durations'
    SPEC = 'spec'
