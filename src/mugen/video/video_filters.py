from enum import Enum
from typing import Any

import mugen.video.detect as v_detect
from mugen.video.VideoSegment import VideoSegment
from mugen.mixins.Filterable import Filter, ContextFilter

""" FILTER FUNCTIONS """


def is_repeat(segment: VideoSegment, memory: Any) -> bool:
    return v_detect.video_segment_is_repeat(segment, video_segments_used=memory)


def has_text(segment: VideoSegment) -> bool:
    return v_detect.video_segment_has_text(segment)


def has_cut(segment: VideoSegment) -> bool:
    return v_detect.video_segment_has_cut(segment)


def has_low_contrast(segment: VideoSegment) -> bool:
    return v_detect.video_segment_has_low_contrast(segment)


""" NEGATION FILTER FUNCTIONS """


def not_is_repeat(*args, **kwargs):
    return not is_repeat(*args, **kwargs)


def not_has_low_contrast(*args, **kwargs):
    return not has_low_contrast(*args, **kwargs)


def not_has_text(*args, **kwargs):
    return not has_text(*args, **kwargs)


def not_has_cut(*args, **kwargs):
    return not has_cut(*args, **kwargs)


class VideoFilter(Enum):
    """
    Attributes
    ----------
    has_text
        video segment has detectable text (letters, words, numbers, etc...). 
        Supports foreign langauges
        
    has_cut
        video segment has a detectable cut between shots
        
    has_low_contrast
        video segment has low contrast (solid color, dark scene, etc...)
        
    is_repeat
        video segment is a repeat of a video segment already used
    """
    # Content Filters
    has_text = Filter(has_text)
    has_cut = Filter(has_cut)
    has_low_contrast = Filter(has_low_contrast)

    not_has_text = Filter(not_has_text)
    not_has_cut = Filter(not_has_cut)
    not_has_low_contrast = Filter(not_has_low_contrast)

    # Context Filters
    is_repeat = ContextFilter(is_repeat)

    not_is_repeat = ContextFilter(not_is_repeat)


# Order is significant when short-circuiting. Order filters from least expensive to most expensive.
VIDEO_FILTERS_DEFAULT = [VideoFilter.not_is_repeat.name, VideoFilter.not_has_low_contrast.name,
                         VideoFilter.not_has_text.name, VideoFilter.not_has_cut.name]

# Remove unavailable filters
if not v_detect.text_detection_available:
    VIDEO_FILTERS_DEFAULT.remove(VideoFilter.not_has_text.name)


