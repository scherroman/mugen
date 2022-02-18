from fractions import Fraction

import pytest

from mugen.utilities import conversion, general


class DummyList(list):
    foo = 1


@pytest.mark.parametrize(
    "a_start, a_end, b_start, b_end, do_overlap",
    [
        (5, 10, 11, 12, False),  # disjoint
        (5, 10, 10, 12, False),  # contiguous
        (5, 10, 9, 12, True),  # overlaps right
        (5, 10, 6, 8, True),  # contained
        (5, 10, 4, 11, True),  # contains
        (5, 10, 5, 10, True),  # equal
        (5, 10, 4, 5, False),  # contiguous
        (5, 10, 4, 6, True),  # overlaps left
    ],
)
def test_ranges_overlap(a_start, a_end, b_start, b_end, do_overlap):
    assert general.check_if_ranges_overlap(a_start, a_end, b_start, b_end) == do_overlap


@pytest.mark.parametrize(
    "float_var, expected_fraction",
    [
        (0.5, Fraction(numerator=1, denominator=2)),
        (1 / 3, Fraction(numerator=1, denominator=3)),
        (5, Fraction(numerator=5, denominator=1)),
    ],
)
def test_float_to_fraction(float_var, expected_fraction):
    assert conversion.float_to_fraction(float_var) == expected_fraction


@pytest.mark.parametrize(
    "slices, length, expected_slices",
    [
        ([slice(1, 2)], 0, [slice(0, 1), slice(1, 2)]),
        ([slice(2, 3)], 2, [slice(0, 2), slice(2, 3)]),
        ([slice(0, 8)], 2, [slice(0, 8)]),
        ([slice(1, 3)], 5, [slice(0, 1), slice(1, 3), slice(3, 5)]),
        ([slice(0, 3), slice(3, 4)], 5, [slice(0, 3), slice(3, 4), slice(4, 5)]),
        (
            [slice(1, 3), slice(5, 7)],
            8,
            [slice(0, 1), slice(1, 3), slice(3, 5), slice(5, 7), slice(7, 8)],
        ),
    ],
)
def test_fill_slices(slices, length, expected_slices):
    assert general.fill_slices(slices, length) == expected_slices


@pytest.mark.parametrize(
    "time, expected_seconds",
    [
        (15.4, 15.4),
        ((1, 21.5), 81.5),
        ((1, 1, 2), 3662),
        (".5", 0.5),
        ("33", 33),
        ("33.045", 33.045),
        ("1:21.5", 81.5),
        ("01:33.045", 93.045),
        ("1:33.045", 93.045),
        ("00:00:33.045", 33.045),
        ("01:01:33.045", 3693.045),
        ("01:01:33.5", 3693.5),
        ("01:01:33,5", 3693.5),
    ],
)
def test_time_to_seconds(time, expected_seconds):
    assert conversion.time_to_seconds(time) == expected_seconds


@pytest.mark.parametrize(
    "seconds, expected_time_code",
    [(25, "00:00:25.000"), (500.45, "00:08:20.450"), (50000.085, "13:53:20.085")],
)
def test_seconds_to_time_code(seconds, expected_time_code):
    assert conversion.seconds_to_time_code(seconds) == expected_time_code


@pytest.mark.parametrize(
    "hex_value, expected_rgb",
    [
        ("#000000", [0, 0, 0]),
        ("#ffffff", [255, 255, 255]),
        ("#3563df", [53, 99, 223]),
        ("#FF4500", [255, 69, 0]),
    ],
)
def test_hex_to_rgb(hex_value, expected_rgb):
    assert conversion.hex_to_rgb(hex_value) == expected_rgb


@pytest.mark.parametrize(
    "color, expected_hex_code",
    [("#123456", "#123456"), ("black", "#000000"), ("white", "#ffffff")],
)
def test_color_to_hex_code(color, expected_hex_code):
    assert conversion.color_to_hex_code(color) == expected_hex_code
