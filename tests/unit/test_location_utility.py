from fractions import Fraction

import pytest

import mugen.location_utility as loc_util


@pytest.mark.parametrize("locations, expected_intervals", [
    ([], []),
    ([6], [6]),
    ([5, 10, 15, 25, 26], [5, 5, 5, 10, 1])
])
def test_intervals_from_locations(locations, expected_intervals):
    assert loc_util.intervals_from_locations(locations) == expected_intervals


@pytest.mark.parametrize("intervals, expected_locations", [
    ([], []),
    ([6], [6]),
    ([5, 5, 5, 10, 1], [5, 10, 15, 25, 26])
])
def test_locations_from_intervals(intervals, expected_locations):
    assert loc_util.locations_from_intervals(intervals) == expected_locations


@pytest.mark.parametrize("locations, pieces_per_split, expected_locations", [
    ([], 2, []),
    ([6], 3, [6]),
    ([6, 12, 18, 20, 30], 2, [6, 9, 12, 15, 18, 19, 20, 25, 30])
])
def test_split_locations(locations, pieces_per_split, expected_locations):
    assert loc_util.split_locations(locations, pieces_per_split) == expected_locations


@pytest.mark.parametrize("locations, locations_per_combo, offset, expected_locations", [
    ([], 5, 0, []),
    ([6], 3, 0, [6]),
    ([6, 12], 3, 0, [6]),
    ([6, 12, 18, 20, 30], 2, 0, [6, 18, 30]),
    ([6, 12, 18, 20, 30], 2, 1, [12, 20]),
    ([6, 12, 18, 20, 30], 3, 0, [6, 20])
])
def test_merge_locations(locations, locations_per_combo, offset, expected_locations):
    assert loc_util.merge_locations(locations, locations_per_combo, offset) == expected_locations


@pytest.mark.parametrize("intervals, expected_start_locations, expected_end_locations", [
    ([], [], []),
    ([2], [0], [2]),
    ([1, 2, 5, 10], [0, 1, 3, 8], [1, 3, 8, 18]),
])
def test_start_end_locations_from_intervals(intervals, expected_start_locations, expected_end_locations):
    assert loc_util.start_end_locations_from_intervals(intervals) == (expected_start_locations, expected_end_locations)


@pytest.mark.parametrize("locations, speed_multiplier, speed_multiplier_offset, expected_locations", [
    ([6, 12, 18, 24], 1, None, [6, 12, 18, 24]),
    ([6, 12, 18, 24], 1 / 2, None, [6, 18]),
    ([6, 12, 18, 24], 2, None, [6, 9, 12, 15, 18, 21, 24])
])
def test_speed_multiply_locations(locations, speed_multiplier, speed_multiplier_offset, expected_locations):
    assert (loc_util.speed_multiply_locations(locations, speed_multiplier, speed_multiplier_offset) ==
            expected_locations)


@pytest.mark.parametrize("locations, offset, expected_locations", [
    ([5, 10, 15, 25, 26], .5, [5.5, 10.5, 15.5, 25.5, 26.5]),
    ([5, 10, 15, 25, 26], -1, [4, 9, 14, 24, 25])
])
def test_offset_locations(locations, offset, expected_locations):
    assert loc_util.offset_locations(locations, offset) == expected_locations
