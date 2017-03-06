from enum import Enum

### Globals ###

debug = False

### GENERAL ###

VERSION = "1.0"
HELP = " Please review supported inputs and values on the help menu via --help"

class FileType(str, Enum):
    AUDIO = 'audio'
    VIDEO = 'video'
    SPEC = 'spec'

### VIDEO ###

DEFAULT_VIDEO_CRF = 18
MOVIEPY_FPS = 24
MOVIEPY_CODEC = 'libx264'
MOVIEPY_AUDIO_BITRATE = '320K'
ESSENTIA_BITRATE = 320

class VideoTrait(str, Enum):
    IS_REPEAT = 'is_repeat'
    HAS_TEXT = 'has_text'
    HAS_SCENE_CHANGE = 'has_scene_change'
    HAS_SOLID_COLOR = 'has_solid_color'

### TRACKS ###

class AudioTrack(str, Enum):
    CUT_LOCATIONS = 'cut_locations'

class SubtitlesTrack(str, Enum):
    SEGMENT_NUMBERS = 'segment_numbers'
    SEGMENT_DURATIONS = 'segment_durations'
    SPEC = 'spec'

### PATHS ###

TEMP_PATH_BASE = 'temp/'
TEMP_MOVIEPY_AUDIOFILE = TEMP_PATH_BASE + 'moviepy_temp_audio.mp3'

OUTPUT_PATH_BASE = 'output/'
MUSIC_VIDEO_NAME_DEFAULT = 'music_video'
VIDEO_OUTPUT_EXTENSION = '.mkv'
SUBTITLES_EXTENSION = '.srt'
SPEC_EXTENSION = '.json'
ESSENTIA_ONSETS_AUDIO_EXTENSION = '.wav'

SEGMENTS_PATH_BASE = OUTPUT_PATH_BASE + 'segments/'
RS_PATH_BASE = OUTPUT_PATH_BASE + 'rejected_segments/'
RS_PATH_REPEAT = RS_PATH_BASE + VideoTrait.IS_REPEAT + '/'
RS_PATH_SCENE_CHANGE = RS_PATH_BASE + VideoTrait.HAS_SCENE_CHANGE + '/'
RS_PATH_TEXT_DETECTED = RS_PATH_BASE + VideoTrait.HAS_TEXT + '/'
RS_PATH_SOLID_COLOR = RS_PATH_BASE + VideoTrait.HAS_SOLID_COLOR + '/'