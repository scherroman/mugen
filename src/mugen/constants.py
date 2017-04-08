from enum import Enum

VERSION = "0.1.0"


class FileType(str, Enum):
    AUDIO = 'audio'
    VIDEO = 'video'
    SPEC = 'spec'

