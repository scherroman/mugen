from enum import Enum

""" GLOBALS """

debug = False

""" GENERAL """

VERSION = "0.1.0"
HELP = " Please review supported inputs and values on the help menu via --help"
MUSIC_VIDEO_NAME_DEFAULT = 'music_video'

class FileType(str, Enum):
    AUDIO = 'audio'
    VIDEO = 'video'
    SPEC = 'spec'

""" AUDIO """

DEFAULT_AUDIO_BITRATE = 320

""" VIDEO """

DEFAULT_VIDEO_CRF = 18
DEFAULT_VIDEO_FPS = 24
DEFAULT_VIDEO_CODEC = 'libx264'

class VideoTrait(str, Enum):
    IS_REPEAT = 'is_repeat'
    HAS_TEXT = 'has_text'
    HAS_SCENE_CHANGE = 'has_scene_change'
    HAS_SOLID_COLOR = 'has_solid_color'

""" TRACKS """

class AudioTrack(str, Enum):
    CUT_LOCATIONS = 'cut_locations'

class SubtitlesTrack(str, Enum):
    SEGMENT_NUMBERS = 'segment_numbers'
    SEGMENT_DURATIONS = 'segment_durations'
    SPEC = 'spec'