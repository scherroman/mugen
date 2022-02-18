# project module marker

from mugen.audio.Audio import Audio
from mugen.mixins.Filterable import ContextFilter, Filter
from mugen.version import __version__
from mugen.video.filters import VideoFilter
from mugen.video.MusicVideo import MusicVideo
from mugen.video.MusicVideoGenerator import MusicVideoGenerator
from mugen.video.segments.ColorSegment import ColorSegment
from mugen.video.segments.ImageSegment import ImageSegment
from mugen.video.segments.VideoSegment import VideoSegment
from mugen.video.sources.ColorSource import ColorSource
from mugen.video.sources.ImageSource import ImageSource
from mugen.video.sources.SourceSampler import SourceSampler
from mugen.video.sources.VideoSource import VideoSource, VideoSourceList

__all__ = [
    Audio,
    ContextFilter,
    Filter,
    __version__,
    VideoFilter,
    MusicVideo,
    MusicVideoGenerator,
    ColorSegment,
    ImageSegment,
    VideoSegment,
    ColorSource,
    ImageSource,
    SourceSampler,
    VideoSource,
    VideoSourceList,
]
