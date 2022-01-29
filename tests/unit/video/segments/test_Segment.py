import pytest

from tests.unit.video.segments.test_ColorSegment import get_orange_segment


@pytest.mark.parametrize("segment, aspect_ratio, expected_dimensions", [
    (get_orange_segment(), 16/9, (300, 168)),
    (get_orange_segment(), 9/16, (168, 300)),
    (get_orange_segment(), 1, (300, 300))
])
def test_crop_to_aspect_ratio(segment, aspect_ratio, expected_dimensions):
    assert segment.crop_to_aspect_ratio(aspect_ratio).dimensions == expected_dimensions


@pytest.mark.parametrize("segment, dimensions, expected_dimensions", [
    (get_orange_segment(), (1920, 1080), (1920, 1080)),
    (get_orange_segment(), (200, 100), (200, 100)),
    (get_orange_segment(), (300, 300), (300, 300))
])
def test_crop_scale(segment, dimensions, expected_dimensions):
    assert segment.crop_scale(dimensions).dimensions == expected_dimensions
