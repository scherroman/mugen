from enum import Enum

from ..constants import Track

DEFAULT_AUDIO_BITRATE = 320
DEFAULT_AUDIO_CODEC = 'mp3'


class AudioTrack(Track):
    CUT_LOCATIONS = 'cut_locations'
