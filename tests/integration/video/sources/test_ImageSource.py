import pytest

from mugen.video.sources.ImageSource import ImageSource
from tests import DATA_PATH


def get_dark_image_source() -> ImageSource:
    return ImageSource(f'{DATA_PATH}/image/dark_image.jpg')


def test_sample__has_correct_duration():
    assert get_dark_image_source().sample(1).duration == pytest.approx(1)
