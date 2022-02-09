import pytest

from mugen.video.sources.ImageSource import ImageSource

from tests import DARK_IMAGE_PATH


def get_dark_image_source() -> ImageSource:
    return ImageSource(DARK_IMAGE_PATH)


def test_sample__has_correct_duration():
    assert get_dark_image_source().sample(1).duration == pytest.approx(1)
