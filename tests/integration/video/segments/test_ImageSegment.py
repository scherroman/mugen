import pytest

from mugen.video.segments.ImageSegment import ImageSegment

from tests import DATA_PATH


@pytest.fixture
def tatami_segment() -> ImageSegment:
    return ImageSegment(f'{DATA_PATH}/image/tatami.jpg')
