import pytest

from mugen.video.segments.ColorSegment import ColorSegment


@pytest.fixture
def black_segment() -> ColorSegment:
    return ColorSegment('black', 1, (720, 540))


@pytest.fixture
def white_segment() -> ColorSegment:
    return ColorSegment('white', 1, (1920, 1080))


@pytest.fixture
def orange_segment() -> ColorSegment:
    return ColorSegment('#FF4500', 1, (300, 300))