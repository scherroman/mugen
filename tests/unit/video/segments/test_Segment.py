import pytest

from .test_ColorSegment import orange_segment


@pytest.mark.parametrize("segment, aspect_ratio, expected_dimensions", [
    (orange_segment(), 16/9, (300, 168)),
    (orange_segment(), 9/16, (168, 300)),
    (orange_segment(), 1, (300, 300))
])
def test_crop_to_aspect_ratio(segment, aspect_ratio, expected_dimensions):
    assert segment.crop_to_aspect_ratio(aspect_ratio).dimensions == expected_dimensions


@pytest.mark.parametrize("segment, dimensions, expected_dimensions", [
    (orange_segment(), (1920, 1080), (1920, 1080)),
    (orange_segment(), (200, 100), (200, 100)),
    (orange_segment(), (300, 300), (300, 300))
])
def test_crop_scale(segment, dimensions, expected_dimensions):
    assert segment.crop_scale(dimensions).dimensions == expected_dimensions
