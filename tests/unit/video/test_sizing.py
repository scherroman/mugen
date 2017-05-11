import pytest

import mugen.video.sizing as v_sizing
from mugen.video.sizing import Dimensions


@pytest.fixture
def dimensions_4_3():
    return Dimensions(720, 540)


@pytest.fixture
def dimensions_16_9():
    return Dimensions(1920, 1080)


@pytest.fixture
def dimensions_21_9():
    return Dimensions(1920, 822)


@pytest.fixture
def list_of_dimensions():
    return [dimensions_16_9(), dimensions_4_3(), dimensions_21_9()]


@pytest.mark.parametrize("dimensions, desired_aspect_ratio, expected_aspect_ratio", [
    (dimensions_16_9(), 16/9, (1920, 1080)),
    (dimensions_16_9(), 4/3, (1440, 1080)),
    (dimensions_4_3(), 16/9, (720, 405))
])
def test_crop_dimensions_to_aspect_ratio(dimensions, desired_aspect_ratio, expected_aspect_ratio):
    assert v_sizing.crop_dimensions_to_aspect_ratio(dimensions, desired_aspect_ratio) == expected_aspect_ratio


@pytest.mark.parametrize("dimensions, desired_aspect_ratio, expected_coordinates", [
    (dimensions_16_9(), 16/9, (0, 0, 1920, 1080)),
    (dimensions_16_9(), 4/3, (240, 0, 1680, 1080)),
    (dimensions_4_3(), 16/9, (0, 67.5, 720, 472.5))
])
def test_crop_coordinates_for_aspect_ratio(dimensions, desired_aspect_ratio, expected_coordinates):
    assert v_sizing.crop_coordinates_for_aspect_ratio(dimensions, desired_aspect_ratio) == expected_coordinates


@pytest.mark.parametrize("dimensions_list, default, expected_dimensions", [
    (list_of_dimensions(), None, (1920, 1080)),
    ([], "default", "default")
])
def test_largest_dimensions(dimensions_list, default, expected_dimensions):
    assert v_sizing.largest_dimensions(dimensions_list, default) == expected_dimensions


@pytest.mark.parametrize("dimensions_list, desired_aspect_ratio, default, expected_dimensions", [
    ([], 16/9, "default", "default"),
    (list_of_dimensions(), 4/3, None, (1440, 1080)),
    (list_of_dimensions(), 16/9, None, (1920, 1080)),
    (list_of_dimensions(), 21/9, None, (1920, 822))
])
def test_largest_dimensions_for_aspect_ratio(dimensions_list, desired_aspect_ratio, default, expected_dimensions):
    assert v_sizing.largest_dimensions_for_aspect_ratio(dimensions_list, desired_aspect_ratio,
                                                        default) == expected_dimensions
