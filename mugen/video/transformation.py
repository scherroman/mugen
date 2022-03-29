from typing import List, Tuple

import mugen.video.sizing as sizing
from mugen.video.effects import Crossfade
from mugen.video.segments.Segment import Segment
from mugen.video.sizing import Dimensions


def crop_to_aspect_ratio(segment: Segment, aspect_ratio: float) -> Segment:
    """
    Returns
    -------
    A new Segment, cropped as necessary to reach specified aspect ratio
    """
    segment = segment.copy()

    if segment.aspect_ratio != aspect_ratio:
        # Crop video to match desired aspect ratio
        x1, y1, x2, y2 = sizing.crop_coordinates_for_aspect_ratio(
            segment.dimensions, aspect_ratio
        )
        segment = segment.crop(x1=x1, y1=y1, x2=x2, y2=y2)

    return segment


def crop_scale(segment: Segment, dimensions: Tuple[int, int]) -> Segment:
    """
    Returns
    -------
    A new Segment, cropped and/or scaled as necessary to reach specified dimensions
    """
    segment = segment.copy()
    dimensions = Dimensions(*dimensions)

    if segment.aspect_ratio != dimensions.aspect_ratio:
        # Crop segment to match aspect ratio
        segment = crop_to_aspect_ratio(segment, dimensions.aspect_ratio)

    if segment.dimensions != dimensions:
        # Resize segment to reach final dimensions
        segment = segment.resize(dimensions)

    return segment


def add_effect_buffers(segments: List[Segment]):
    """
    Adds buffers for video effects to a list of segments
    """
    buffered_segments = []
    for index, segment in enumerate(segments):
        buffered_segments.append(segment)

        if index == len(segments) - 1:
            continue

        next_segment = segments[index + 1]
        segment_buffers = _get_effect_buffers(segment, next_segment)
        buffered_segments.extend(segment_buffers)

    return buffered_segments


def _get_effect_buffers(segment: Segment, next_segment: Segment):
    effect_buffers = []
    for effect in next_segment.effects:
        if isinstance(effect, Crossfade):
            effect_buffers.append(effect.buffer(segment))

    return effect_buffers


def apply_effects(segment) -> Segment:
    """
    Composes the segment, applying all effects

    Returns
    -------
    A new segment with all effects applied
    """
    segment = segment.copy()
    for effect in segment.effects:
        segment = effect.apply(segment)

    return segment


def apply_contextual_effects(segment: Segment, previous_segment: Segment):
    for effect in segment.effects:
        segment = effect.apply(segment, previous_segment)

    return segment
