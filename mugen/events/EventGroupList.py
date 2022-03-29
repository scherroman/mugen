from itertools import zip_longest
from typing import List, Optional, Union

from mugen import lists
from mugen.constants import TIME_FORMAT
from mugen.events.EventList import EventList
from mugen.lists import MugenList


class EventGroupList(MugenList):
    """
    An alternate, more useful representation for a list of EventLists
    """

    _selected_groups: List[EventList]

    def __init__(
        self,
        groups: Optional[Union[List[EventList], List[List[TIME_FORMAT]]]] = None,
        *,
        selected: List[EventList] = None,
    ):
        """
        Parameters
        ----------
        groups

        selected
            A subset of groups to track
        """
        if groups is None:
            groups = []

        for index, group in enumerate(groups):
            if not isinstance(group, EventList):
                groups[index] = EventList(group)

        super().__init__(groups)

        self._selected_groups = selected or []

    def __repr__(self):
        group_reprs = []
        index_count = 0
        for group in self:
            group_indexes = range(index_count, index_count + len(group) - 1)
            group_reprs.append(
                group.list_repr(
                    group_indexes, True if group in self.selected_groups else False
                )
            )
            index_count += len(group)
        return super().pretty_repr(group_reprs)

    @property
    def end(self):
        return self[-1].end if self else None

    @property
    def selected_groups(self) -> "EventGroupList":
        """
        Returns
        -------
        Selected groups
        """
        return EventGroupList([group for group in self._selected_groups])

    @property
    def unselected_groups(self) -> "EventGroupList":
        """
        Returns
        -------
        Unselected groups
        """
        return EventGroupList(
            [group for group in self if group not in self.selected_groups]
        )

    def speed_multiply(
        self, speeds: List[float], offsets: Optional[List[float]] = None
    ):
        """
        Speed multiplies event groups, in order

        See :meth:`~mugen.events.EventList.speed_multiply` for further information.
        """
        if offsets is None:
            offsets = []

        for group, speed, offset in zip_longest(self, speeds, offsets):
            group.speed_multiply(speed if speed is not None else 1, offset)

    def flatten(self) -> EventList:
        """
        Flattens the EventGroupList back into an EventList.

        Returns
        -------
        A flattened EventList for this EventGroupList
        """
        return EventList(lists.flatten(self), end=self.end)
