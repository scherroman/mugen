from fractions import Fraction
from functools import wraps
from typing import List, Union, Optional as Opt, Tuple

import numpy as np

from mugen.utility import convert_to_fraction, validate_speed_multiplier

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


def split_locations(locations: List[float], pieces_per_split: int) -> List[float]:
    """
    Splits locations up to form shorter intervals
    
    Parameters
    ----------
    locations
    
    pieces_per_split
        Number of pieces to split each location into

    Returns
    -------
    Split locations
    """
    splintered_locations = []

    for index, location in enumerate(locations):
        splintered_locations.append(location)

        if index == len(locations) - 1:
            continue

        next_location = locations[index + 1]
        interval = next_location - location
        interval_piece = interval / pieces_per_split

        for _ in range(pieces_per_split - 1):
            location += interval_piece
            splintered_locations.append(location)

    return splintered_locations


def merge_locations(locations: List[float], pieces_per_merge: int, offset: Opt[int] = None) -> List[float]:
    """
    Merges adjacent locations to form longer intervals

    Parameters
    ----------
    locations
    
    pieces_per_merge
        Number of adjacent locations to merge at a time
        
    offset
        Offset for the merging of locations

    Returns
    -------
    Merged locations
    """
    if offset is None:
        offset = 0

    combined_locations = []

    for index, location in enumerate(locations):
        if (index - offset) % pieces_per_merge == 0:
            combined_locations.append(location)

    return combined_locations


def start_end_locations_from_intervals(intervals: List[float]) -> Tuple[List[float], List[float]]:
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
    for index, duration in enumerate(intervals):
        start_time = running_duration
        end_time = start_time + duration

        start_locations.append(start_time)
        end_locations.append(end_time)

        running_duration += duration

    return start_locations, end_locations


def offset_locations(locations: List[float], offset: float) -> List[float]:
    return [location + offset for location in locations]


@validate_speed_multiplier
@convert_to_fraction('speed_multiplier')
def speed_multiply_locations(locations: Union[List[float], np.ndarray],
                             speed_multiplier: Union[float, Fraction],
                             speed_multiplier_offset: Opt[int] = None) -> List[float]:
    if speed_multiplier > 1:
        locations = split_locations(locations, speed_multiplier.numerator)
    elif speed_multiplier < 1:
        locations = merge_locations(locations, speed_multiplier.denominator,
                                    speed_multiplier_offset)

    return locations
