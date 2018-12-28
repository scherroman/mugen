import pytest

from mugen.video.sources.ImageSource import ImageSource
from tests import DATA_PATH


@pytest.fixture
def tatami_source() -> ImageSource:
    return ImageSource(f'{DATA_PATH}/image/tatami.jpg')


def test_sample():
    image_source = tatami_source()

    assert image_source.sample(1).duration == pytest.approx(1)
