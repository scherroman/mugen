from fractions import Fraction
from functools import wraps
from itertools import groupby
from operator import attrgetter
from typing import List, Optional, Tuple, Union

from mugen.constants import TIME_FORMAT
from mugen.events.Event import Event
from mugen.events.utilities import merge_events, split_events
from mugen.lists import MugenList
from mugen.utilities import general, location
from mugen.utilities.conversion import convert_float_to_fraction


def requires_end(func):
    """
    Decorator raises error if there is no end specified for the EventList
    """

    @wraps(func)
    def _requires_end(self, *args, **kwargs):
        if not self.end:
            raise ValueError(
                f"EventList's {func} method requires the 'end' attribute to be set."
            )

        return func(self, *args, **kwargs)

    return _requires_end


class EventList(MugenList):
    """
    A list of Events which occur in some time sequence
    """

    end: Optional[float]

    def __init__(
        self,
        events: Optional[List[Union[Event, TIME_FORMAT]]] = None,
        *,
        end: TIME_FORMAT = None,
    ):
        """
        Parameters
        ----------
        events
            events which occur in the time sequence

        end
            duration of the time sequence
        """
        if events is None:
            events = []

        for index, event in enumerate(events):
            if not isinstance(event, Event):
                events[index] = Event(event)

        self.end = end

        super().__init__(events)

    def __eq__(self, other):
        return super().__eq__(other) and self.end == other.end

    def __add__(self, rhs):
        return type(self)((super().__add__(rhs)), end=rhs.end)

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        if isinstance(item, slice):
            return type(self)(result, end=self.end)
        else:
            return result

    def __repr__(self):
        event_reprs = [event.index_repr(index) for index, event in enumerate(self)]
        pretty_repr = super().pretty_repr(event_reprs)
        return f"<{pretty_repr}, end: {self.end}>"

    def list_repr(self, indexes: range, selected: bool):
        """
        Repr for use in lists
        """
        return (
            f"<{self.__class__.__name__} {indexes.start}-{indexes.stop} ({len(self)}), "
            f"type: {self.type}, selected: {selected}>"
        )

    @property
    def type(self) -> Union[str, None]:
        if len(self) == 0:
            return None
        elif len(set([event.__class__.__name__ for event in self])) == 1:
            return self[0].__class__.__name__
        else:
            return "mixed"

    @property
    def locations(self) -> List[float]:
        return [event.location for event in self]

    @property
    def intervals(self) -> List[float]:
        return location.intervals_from_locations(self.locations)

    @property
    def segment_locations(self):
        """
        Returns
        -------
        locations of segments between events
        """
        return [0] + [event.location for event in self]

    @property
    @requires_end
    def segment_durations(self):
        """
        Returns
        -------
        durations of segments between events
        """
        return location.intervals_from_locations(self.locations + [self.end])

    @property
    def durations(self) -> List[float]:
        return [event.duration for event in self]

    @property
    def types(self) -> List[str]:
        return [event.__class__.__name__ for event in self]

    def offset(self, offset: float):
        """
        Offsets all events by the given amount
        """
        for event in self:
            event.location += offset

    @convert_float_to_fraction("speed")
    def speed_multiply(
        self, speed: Union[float, Fraction], offset: Optional[int] = None
    ):
        """
        Speeds up or slows down events by grouping them together or splitting them up.
        For slowdowns, event type group boundaries and isolated events are preserved.

        Parameters
        ----------
        speed
            Factor to speedup or slowdown by.
            Must be of the form x (speedup) or 1/x (slowdown), where x is a natural number.
            Otherwise, 0 to remove all events.

        offset
            Offsets the grouping of events for slowdowns.
            Takes a max offset of x - 1 for a slowdown of 1/x, where x is a natural number
        """
        if speed == 0:
            self.clear()
        elif speed > 1:
            self._split_by_type(speed.numerator)
        elif speed < 1:
            self._merge_by_type(speed.denominator, offset)

    def _split_by_type(self, pieces_per_split: int):
        """
        Splits events of identical type up to form shorter intervals

        Parameters
        ----------
        pieces_per_split
            Number of pieces to split each event into
        """
        splitted_events = EventList()
        type_groups = self.group_by_type()

        for group in type_groups:
            splitted_events.extend(split_events(group, pieces_per_split))

        self[:] = splitted_events

    def _merge_by_type(self, pieces_per_merge: int, offset: int = None):
        """
        Merges adjacent events of identical type to form longer intervals

        Parameters
        ----------
        pieces_per_merge
            Number of adjacent events to merge at a time

        offset
            Offset for the merging of events
        """
        if offset is None:
            offset = 0

        merged_events = EventList()
        type_groups = self.group_by_type()
        for group in type_groups:
            if offset >= len(group):
                merged_events.extend(group)
            else:
                merged_events.extend(merge_events(group, pieces_per_merge, offset))

        self[:] = merged_events

    def group_by_type(self, select_types: List[str] = None):
        """
        Groups events by type

        Attributes
        ----------
        select_types
            A list of types for which to select groups in the resulting EventGroupList.
            If no types are specified, all resulting groups will be selected.

        Returns
        -------
        An EventGroupList partitioned by type
        """
        from mugen.events.EventGroupList import EventGroupList

        if select_types is None:
            select_types = []

        groups = [
            EventList(list(group), end=self.end)
            for _, group in groupby(self, key=attrgetter("__class__"))
        ]
        if not select_types:
            selected_groups = groups
        else:
            selected_groups = [group for group in groups if group.type in select_types]

        return EventGroupList(groups, selected=selected_groups)

    def group_by_slices(self, slices: Tuple[int, int]):
        """
        Groups events by slices.
        Does not support negative indexing.

        Slices explicitly passed in will become selected groups in the resulting EventGroupList.

        Returns
        -------
        An EventGroupList partitioned by slice
        """
        from mugen.events.EventGroupList import EventGroupList

        slices = [slice(sl[0], sl[1]) for sl in slices]

        # Fill in rest of slices
        all_slices = general.fill_slices(slices, len(self))
        target_indexes = [index for index, sl in enumerate(all_slices) if sl in slices]

        # Group events by slices
        groups = [self[sl] for sl in all_slices]
        selected_groups = [
            group for index, group in enumerate(groups) if index in target_indexes
        ]
        groups = EventGroupList(groups, selected=selected_groups)

        return groups
