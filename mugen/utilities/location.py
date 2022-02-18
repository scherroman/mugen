from typing import List, Tuple

"""
Module for Location & Interval manipulation
"""


def intervals_from_locations(locations: List[float]) -> List[float]:
    intervals = []

    previous_location = None
    for index, location in enumerate(locations):
        if index == 0:
            intervals.append(location)
        else:
            intervals.append(location - previous_location)
        previous_location = location

    return intervals


def locations_from_intervals(intervals: List[float]) -> List[float]:
    locations = []
    running_duration = 0
    for index, interval in enumerate(intervals):
        if index < len(intervals):
            running_duration += interval
            locations.append(running_duration)

    return locations


def start_end_locations_from_locations(
    locations: List[float],
) -> Tuple[List[float], List[float]]:
    """
    Calculates the start and end times of each location

    Ex) 5, 10, 15
        start_times == 5, 10, 15
        end_times == 10, 15, 15

    Returns
    -------
    A tuple of start and end times
    """
    start_locations = []
    end_locations = []

    for index, location in enumerate(locations):
        start_time = location
        if index == len(locations) - 1:
            end_time = location
        else:
            end_time = locations[index + 1]

        start_locations.append(start_time)
        end_locations.append(end_time)

    return start_locations, end_locations


def start_end_locations_from_intervals(
    intervals: List[float],
) -> Tuple[List[float], List[float]]:
    """
    Calculates the start and end times of each interval

    Ex) 5, 10, 15
        start_times == 0, 5, 10
        end_times == 5, 10, 15

    Returns
    -------
    A tuple of start and end times
    """
    start_locations = []
    end_locations = []

    running_duration = 0
    for _, duration in enumerate(intervals):
        start_time = running_duration
        end_time = start_time + duration

        start_locations.append(start_time)
        end_locations.append(end_time)

        running_duration += duration

    return start_locations, end_locations
