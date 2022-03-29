import pytest

from mugen.video import sizing
from mugen.video.sizing import Dimensions


def get_4_3_dimensions():
    return Dimensions(720, 540)


def get_16_9_dimensions():
    return Dimensions(1920, 1080)


def get_21_9_dimensions():
    return Dimensions(1920, 822)


def get_list_of_dimensions():
    return [get_16_9_dimensions(), get_4_3_dimensions(), get_21_9_dimensions()]


@pytest.mark.parametrize(
    "dimensions, aspect_ratio, expected_dimensions",
    [
        (get_16_9_dimensions(), 16 / 9, (1920, 1080)),
        (get_16_9_dimensions(), 4 / 3, (1440, 1080)),
        (get_4_3_dimensions(), 16 / 9, (720, 405)),
    ],
)
def test_crop_dimensions_to_aspect_ratio(dimensions, aspect_ratio, expected_dimensions):
    assert (
        sizing.crop_dimensions_to_aspect_ratio(dimensions, aspect_ratio)
        == expected_dimensions
    )


@pytest.mark.parametrize(
    "dimensions, desired_aspect_ratio, expected_coordinates",
    [
        (get_16_9_dimensions(), 16 / 9, (0, 0, 1920, 1080)),
        (get_16_9_dimensions(), 4 / 3, (240, 0, 1680, 1080)),
        (get_4_3_dimensions(), 16 / 9, (0, 67.5, 720, 472.5)),
    ],
)
def test_crop_coordinates_for_aspect_ratio(
    dimensions, desired_aspect_ratio, expected_coordinates
):
    assert (
        sizing.crop_coordinates_for_aspect_ratio(dimensions, desired_aspect_ratio)
        == expected_coordinates
    )


@pytest.mark.parametrize(
    "dimensions_list, desired_aspect_ratio, expected_dimensions",
    [
        (get_list_of_dimensions(), 4 / 3, (1440, 1080)),
        (get_list_of_dimensions(), 16 / 9, (1920, 1080)),
        (get_list_of_dimensions(), 21 / 9, (1920, 822)),
    ],
)
def test_largest_dimensions_for_aspect_ratio__returns_correct_dimensions(
    dimensions_list, desired_aspect_ratio, expected_dimensions
):
    assert (
        sizing.largest_dimensions_for_aspect_ratio(
            dimensions_list, desired_aspect_ratio
        )
        == expected_dimensions
    )


def test_largest_dimensions_for_aspect_ratio__throws_an_error_when_given_an_empty_list():
    with pytest.raises(ValueError):
        sizing.largest_dimensions_for_aspect_ratio([], 16 / 9)
