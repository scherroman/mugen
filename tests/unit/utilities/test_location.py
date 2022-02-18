import pytest

from mugen.utilities import location


@pytest.mark.parametrize(
    "locations, expected_intervals",
    [([], []), ([6], [6]), ([5, 10, 15, 25, 26], [5, 5, 5, 10, 1])],
)
def test_intervals_from_locations(locations, expected_intervals):
    assert location.intervals_from_locations(locations) == expected_intervals


@pytest.mark.parametrize(
    "intervals, expected_locations",
    [([], []), ([6], [6]), ([5, 5, 5, 10, 1], [5, 10, 15, 25, 26])],
)
def test_locations_from_intervals(intervals, expected_locations):
    assert location.locations_from_intervals(intervals) == expected_locations


@pytest.mark.parametrize(
    "locations, expected_start_locations, expected_end_locations",
    [
        ([], [], []),
        ([2], [2], [2]),
        ([0, 1, 2], [0, 1, 2], [1, 2, 2]),
        ([1, 2, 5, 10], [1, 2, 5, 10], [2, 5, 10, 10]),
    ],
)
def test_start_end_locations_from_locations(
    locations, expected_start_locations, expected_end_locations
):
    assert location.start_end_locations_from_locations(locations) == (
        expected_start_locations,
        expected_end_locations,
    )


@pytest.mark.parametrize(
    "intervals, expected_start_locations, expected_end_locations",
    [
        ([], [], []),
        ([2], [0], [2]),
        ([1, 2, 5, 10], [0, 1, 3, 8], [1, 3, 8, 18]),
    ],
)
def test_start_end_locations_from_intervals(
    intervals, expected_start_locations, expected_end_locations
):
    assert location.start_end_locations_from_intervals(intervals) == (
        expected_start_locations,
        expected_end_locations,
    )
