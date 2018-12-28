import pytest

from mugen.video.sources import ColorSource


@pytest.fixture
def black_source() -> ColorSource:
    return ColorSource('black')


@pytest.fixture
def white_source() -> ColorSource:
    return ColorSource('white')


@pytest.fixture
def orange_source() -> ColorSource:
    return ColorSource('#FFA500')


@pytest.fixture
def purple_source() -> ColorSource:
    return ColorSource('#800080')
