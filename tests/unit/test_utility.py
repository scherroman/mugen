from fractions import Fraction

import pytest

import mugen.utility as util


@pytest.mark.parametrize("locations, offset, expected_locations", [
    ([5, 10, 15, 25, 26], .5, [5.5, 10.5, 15.5, 25.5, 26.5]),
    ([5, 10, 15, 25, 26], -1, [4, 9, 14, 24, 25])
])
def test_offset_locations(locations, offset, expected_locations):
    assert util.offset_locations(locations, offset) == expected_locations


@pytest.mark.parametrize("locations, expected_intervals", [
    ([], []),
    ([6], [6]),
    ([5, 10, 15, 25, 26], [5, 5, 5, 10, 1])
])
def test_intervals_from_locations(locations, expected_intervals):
    assert util.intervals_from_locations(locations) == expected_intervals


@pytest.mark.parametrize("intervals, expected_locations", [
    ([], []),
    ([6], [6]),
    ([5, 5, 5, 10, 1], [5, 10, 15, 25, 26])
])
def test_locations_from_intervals(intervals, expected_locations):
    assert util.locations_from_intervals(intervals) == expected_locations


@pytest.mark.parametrize("locations, pieces_per_split, expected_locations", [
    ([], 2, []),
    ([6], 3, [6]),
    ([6, 12, 18, 20, 30], 2, [6, 9, 12, 15, 18, 19, 20, 25, 30])
])
def test_split_locations(locations, pieces_per_split, expected_locations):
    assert util.split_locations(locations, pieces_per_split) == expected_locations


@pytest.mark.parametrize("locations, locations_per_combo, offset, expected_locations", [
    ([], 5, 0, []),
    ([6], 3, 0, [6]),
    ([6, 12], 3, 0, [6]),
    ([6, 12, 18, 20, 30], 2, 0, [6, 18, 30]),
    ([6, 12, 18, 20, 30], 2, 1, [12, 20]),
    ([6, 12, 18, 20, 30], 3, 0, [6, 20])
])
def test_combine_locations(locations, locations_per_combo, offset, expected_locations):
    assert util.merge_locations(locations, locations_per_combo, offset) == expected_locations


@pytest.mark.parametrize("locations, speed_multiplier, speed_multiplier_offset, expected_locations", [
    ([6, 12, 18, 24], 1, None, [6, 12, 18, 24]),
    ([6, 12, 18, 24], 1 / 2, None, [6, 18]),
    ([6, 12, 18, 24], 2, None, [6, 9, 12, 15, 18, 21, 24])
])
def test_split_locations(locations, speed_multiplier, speed_multiplier_offset, expected_locations):
    assert util.locations_after_speed_multiplier(locations, speed_multiplier, speed_multiplier_offset) == \
           expected_locations


@pytest.mark.parametrize("intervals, expected_start_times, expected_end_times", [
    ([], [], []),
    ([2], [0], [2]),
    ([1, 2, 5, 10], [0, 1, 3, 8], [1, 3, 8, 18]),
])
def test_start_end_times_from_durations(intervals, expected_start_times, expected_end_times):
    assert util.start_end_locations_from_intervals(intervals) == (expected_start_times, expected_end_times)


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