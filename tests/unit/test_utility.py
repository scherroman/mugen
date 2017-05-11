from fractions import Fraction

import pytest

import mugen.utility as util


@pytest.mark.parametrize("l, expected_l", [
    ([1, [2, 3], [[4, 5], [6, 7]]], [1, 2, 3, 4, 5, 6, 7])
])
def test_flatten(l, expected_l):
    assert util.flatten(l) == expected_l


@pytest.mark.parametrize("a_start, a_end, b_start, b_end, do_overlap", [
    (5, 10, 11, 12, False),  # disjoint
    (5, 10, 10, 12, False),  # contiguous
    (5, 10, 9, 12, True),    # overlaps right
    (5, 10, 5, 10, True),    # equal
    (5, 10, 6, 8, True),     # contained
    (5, 10, 4, 11, True),    # contains
    (5, 10, 4, 5, False),    # contiguous
    (5, 10, 4, 6, True),     # overlaps left
])
def test_ranges_overlap(a_start, a_end, b_start, b_end, do_overlap):
    assert util.ranges_overlap(a_start, a_end, b_start, b_end) == do_overlap


@pytest.mark.parametrize("float_var, expected_fraction", [
    (.5, Fraction(numerator=1, denominator=2)),
    (1/3, Fraction(numerator=1, denominator=3)),
    (5, Fraction(numerator=5, denominator=1))
])
def test_float_to_fraction(float_var, expected_fraction):
    assert util.float_to_fraction(float_var) == expected_fraction


@pytest.mark.parametrize("time, expected_seconds", [
    (15.4, 15.4),
    ((1, 21.5), 81.5),
    ((1, 1, 2), 3662),
    ('.5', .5),
    ('33', 33),
    ('33.045', 33.045),
    ('01:33.045', 93.045),
    ('00:00:33.045', 33.045),
    ('01:01:33.045', 3693.045),
    ('01:01:33.5', 3693.5),
    ('01:01:33,5', 3693.5)
])
def test_time_to_seconds(time, expected_seconds):
    assert util.time_to_seconds(time) == expected_seconds