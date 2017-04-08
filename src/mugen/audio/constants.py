from enum import Enum

DEFAULT_AUDIO_BITRATE = 320


class AudioTrack(str, Enum):
    CUT_LOCATIONS = 'cut_locations'