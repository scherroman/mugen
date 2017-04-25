from enum import Enum

import mugen.video.detect as v_detect
from mugen.mixins.Filterable import Filter, ContextFilter

""" FILTER FUNCTIONS """


def is_repeat(segment, memory):
    return v_detect.video_segment_is_repeat(segment, video_segments_used=memory)


def has_text(segment):
    return v_detect.video_segment_has_text(segment)


def has_cut(segment):
    return v_detect.video_segment_has_cut(segment)


def has_low_contrast(segment):
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
VIDEO_FILTERS_STANDARD = [VideoFilter.not_is_repeat, VideoFilter.not_has_low_contrast, VideoFilter.not_has_text,
                          VideoFilter.not_has_cut]

# Remove unavailable filters
if not v_detect.text_detection_available:
    VIDEO_FILTERS_STANDARD.remove(VideoFilter.not_has_text)


