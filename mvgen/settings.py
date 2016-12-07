### Globals ###
debug = False
music_video_name = None

### GENERAL ###
HELP = " Please review supported inputs and values on the help menu via --help"

### VIDEO ###
MOVIEPY_FPS = 24
MOVIEPY_CODEC = 'libx264'
MOVIEPY_CRF = "18"
MOVIEPY_AUDIO_BITRATE = '320K'

MIN_EXTREMA_RANGE = 30
DURATION_PRECISION = 17

RS_TYPE_SCENE_CHANGE = 'scene_change'
RS_TYPE_TEXT_DETECTED = 'text_detected'
RS_TYPE_SOLID_COLOR = 'solid_color'

### PATHS ###
OUTPUT_PATH_BASE = 'output/'
OUTPUT_NAME_DEFAULT = 'music_video'
OUTPUT_EXTENSION = '.mp4'
SPEC_EXTENSION = '.json'

SEGMENTS_PATH_BASE = 'segments/'
RS_PATH_BASE = 'rejected_segments/'
RS_PATH_SCENE_CHANGE = RS_PATH_BASE + RS_TYPE_SCENE_CHANGE + '/'
RS_PATH_TEXT_DETECTED = RS_PATH_BASE + RS_TYPE_TEXT_DETECTED + '/'
RS_PATH_SOLID_COLOR = RS_PATH_BASE + RS_TYPE_SOLID_COLOR +'/'