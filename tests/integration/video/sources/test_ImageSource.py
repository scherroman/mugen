import pytest

from mugen.video.sources.ImageSource import ImageSource
from tests import LANDSCAPE_IMAGE_PATH


def get_landscape_image_source() -> ImageSource:
    return ImageSource(LANDSCAPE_IMAGE_PATH)


def test_sample__has_correct_duration():
    assert get_landscape_image_source().sample(1).duration == pytest.approx(1)
