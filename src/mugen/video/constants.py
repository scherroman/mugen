import numpy as np

from mugen.constants import Track

DEFAULT_VIDEO_CRF = 18
DEFAULT_VIDEO_FPS = 24
DEFAULT_VIDEO_CODEC = 'libx264'

LIST_3D = np.ndarray

OUTPUT_PATH_BASE = 'output'
SEGMENTS_DIRECTORY = 'video_segments'
RS_DIRECTORY = 'rejected_video_segments'

VIDEO_OUTPUT_EXTENSION = '.mkv'
SPEC_EXTENSION = '.json'


class SubtitleTrack(Track):
    SEGMENT_NUMBERS = 'segment_numbers'
    SEGMENT_DURATIONS = 'segment_durations'
    SPEC = 'spec'
