import copy
from enum import Enum
from fractions import Fraction
from typing import List, Optional as Opt, Union

from mugen.utility import convert_to_fraction, validate_speed_multiplier


class EventType(str, Enum):
    """
    Type of an event
    """
    pass


class EventsMode(str, Enum):
    """
    Method of generating events
    """
    pass


class Event:
    """
    Location at which an event occurs in some time sequence (i.e a song, or music video)

    Attributes
    ----------
    location
        location of the event in the time sequence
        
    duration
        duration of the event
        
    type
        type of event
    """
    location: float
    duration: int = 0
    type: Opt[str] = None

    def __init__(self, location: float, *, duration: Opt[int] = None, type: Opt[str] = None):
        self.location = location
        if duration is not None:
            self.duration = duration
        if type is not None:
            self.type = type

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other


class ColorEvent(Event):
    """
    An Event which uses a color
    
    Attributes
    ----------
    color
        Hex color code representing a color. ex) #003366 (Midnight Blue)
    """
    color: str

    def __init__(self, color: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color


class EventsModifier(str, Enum):
    """
    Parameters
    ----------
    offset : int
        Offsets events by the given amount
        
    speed_multiplier : float
        Speeds up or slows down events by grouping them together or splitting them up.
        Must be of the form x (speedup) or 1/x (slowdown), where x is a natural number.
                      
    speed_multiplier_offset : int 
        Offsets the grouping of events for slowdown speed_multipliers. 
        Takes a max offset of x - 1 for a slowdown of 1/x, where x is a natural number.
    """
    OFFSET = 'offset'
    SPEED_MULTIPLIER = 'speed_multiplier'
    SPEED_MULTIPLIER_OFFSET = 'speed_multiplier_offset'


class EventList(list):
    """
    A list of Events
    """

    def __init__(self, events: Opt[List[Event]] = None):
        super().__init__()
        if events:
            self.extend(events)

    @classmethod
    def from_locations(cls, locations: List[float], *, type: Opt[EventType] = None) -> 'EventList':
        return EventList([Event(location, type=type) for location in locations])

    @property
    def locations(self) -> List[float]:
        return [event.location for event in self]

    @property
    def types(self) -> List[str]:
        return [event.type for event in self]

    @property
    def types_are_uniform(self) -> bool:
        return len(set(self.types)) <= 1

    def offset(self, offset: float):
        """
        Offsets all events by the given amount         
        """
        for event in self:
            event.location += offset

    @validate_speed_multiplier
    @convert_to_fraction('speed_multiplier')
    def speed_multiply(self, speed_multiplier: Union[float, Fraction],
                       speed_multiplier_offset: Opt[int] = None):
        """
        Speeds up or slows down events by grouping them together or splitting them up

        Parameters
        ----------
        speed_multiplier 
            Factor to speedup or slowdown by. 
            Must be of the form x (speedup) or 1/x (slowdown), where x is a natural number
            
        speed_multiplier_offset
            Offsets the grouping of events for slowdown speed_multipliers. 
            Takes a max offset of x - 1 for a slowdown of 1/x, where x is a natural number
        """
        if speed_multiplier > 1:
            self._split(speed_multiplier.numerator)
        elif speed_multiplier < 1:
            self._merge(speed_multiplier.denominator, speed_multiplier_offset)

    def _split(self, pieces_per_split: int):
        """
        Splits events up to form shorter intervals

        Parameters
        ----------
        pieces_per_split
            Number of pieces to split each event into
        """
        splintered_events = EventList()
        
        for index, event in enumerate(self):
            splintered_events.append(event)

            if index == len(self) - 1:
                # Skip last event
                continue

            next_event = self[index + 1]
            interval = next_event.location - event.location
            interval_piece = interval / pieces_per_split

            location = event.location
            for _ in range(pieces_per_split - 1):
                location += interval_piece
                event_splinter = copy.deepcopy(event)
                event_splinter.location = location
                splintered_events.append(event_splinter)

        self.clear()
        self.extend(splintered_events)

    def _merge(self, pieces_per_merge: int, offset: Opt[int] = None):
        """
        Merges adjacent events to form longer intervals

        Parameters
        ----------
        pieces_per_merge 
            Number of adjacent events to merge at a time
            
        offset
            Offset for the merging of events
        """
        if offset is None:
            offset = 0

        combined_events = EventList()

        for index, event in enumerate(self):
            if (index - offset) % pieces_per_merge == 0:
                combined_events.append(event)

        self.clear()
        self.extend(combined_events)

    def modify(self, event_modifiers: dict):
        """
        Applies one or more modifiers to a list of events

        Parameters
        ----------
        event_modifiers
            Modifiers to apply to events. 
            See :class:`~mugen.events.EventsModifer` for available parameters
        """
        speed_multiplier = event_modifiers.get(EventsModifier.SPEED_MULTIPLIER)
        speed_multiplier_offset = event_modifiers.get(EventsModifier.SPEED_MULTIPLIER_OFFSET)
        offset = event_modifiers.get(EventsModifier.OFFSET)

        if speed_multiplier is not None:
            self.speed_multiply(speed_multiplier, speed_multiplier_offset)
        if offset is not None:
            self.offset(offset)









