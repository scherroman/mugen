import copy
from typing import List

from mugen.events.Event import Event


def split_events(events: List[Event], pieces_per_split: int):
    """
    Splits events up to form shorter intervals

    Parameters
    ----------
    pieces_per_split
        Number of pieces to split each event into
    """
    split_events = []
    for index, event in enumerate(events):
        split_events.append(event)

        if index == len(events) - 1:
            continue

        next_event = events[index + 1]
        interval = next_event.location - event.location
        interval_piece = interval / pieces_per_split

        location = event.location
        for _ in range(pieces_per_split - 1):
            location += interval_piece
            split_event = copy.deepcopy(event)
            split_event.location = location
            split_events.append(split_event)

    return split_events


def merge_events(events: List[Event], pieces_per_merge: int, offset: int = 0):
    """
    Merges adjacent events to form longer intervals

    Parameters
    ----------
    events
        Events to merge
    pieces_per_merge
        Number of adjacent events to merge at a time

    offset
        Offset for the merging of events
    """
    merged_events = []
    for index, event in enumerate(events):
        if (index - offset) % pieces_per_merge == 0:
            merged_events.append(event)

    return merged_events
