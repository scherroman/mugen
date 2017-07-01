import pytest

from mugen.events import Event, EventList, EventGroupList


@pytest.fixture
def events() -> EventList:
    return EventList([Event(6, type='silence'),
                      Event(12, type='beat'),
                      Event(18, type='beat'),
                      Event(24, type='beat'),
                      Event(30, type='silence')])


@pytest.fixture
def events_grouped_by_type() -> EventGroupList:
    return EventGroupList([EventList([Event(6, type='silence')]),
                           EventList([Event(12, type='beat'),
                                      Event(18, type='beat'),
                                      Event(24, type='beat')]),
                           EventList([Event(30, type='silence')])])


@pytest.fixture
def events_speed_multiplied_2x() -> EventList:
    return EventList([Event(6, type='silence'),
                      Event(12, type='beat'), Event(15, type='beat'),
                      Event(18, type='beat'), Event(21, type='beat'),
                      Event(24, type='beat'),
                      Event(30, type='silence')])


@pytest.fixture
def events_speed_multiplied_1_2x() -> EventList:
    return EventList([Event(6, type='silence'),
                      Event(12, type='beat'),
                      Event(24, type='beat'),
                      Event(30, type='silence')])


@pytest.fixture
def events_speed_multiplied_1_2x_offset_1() -> EventList:
    return EventList([Event(6, type='silence'),
                      Event(18, type='beat'),
                      Event(30, type='silence')])


@pytest.fixture
def events_speed_multiplied_1_3x() -> EventList:
    return EventList([Event(6, type='silence'),
                      Event(12, type='beat'),
                      Event(30, type='silence')])


def test_event_list__initializes_non_uniform_inputs_successfully():
    EventList([1, 2, 3, Event(4, type="beat")])


@pytest.mark.parametrize("events, speed, offset, expected_events", [
    (EventList([]), 5, None, []),
    (EventList([6]), 0, None, EventList([])),
    (EventList([6]), 3, None, EventList([6])),
    (EventList([6, 12]), 1 / 3, None, EventList([6])),
    (EventList([1, 2, 3, 4, 5, 6, 7, 8]), 1 / 2, None, EventList([1, 3, 5, 7])),
    (events(), 1, None, events()),
    (events(), 1 / 2, None, events_speed_multiplied_1_2x()),
    (events(), 1 / 2, 1, events_speed_multiplied_1_2x_offset_1()),
    (events(), 1 / 3, None, events_speed_multiplied_1_3x()),
    (events(), 2, None, events_speed_multiplied_2x())
])
def test_speed_multiply_events(events, speed, offset, expected_events):
    events.speed_multiply(speed, offset)
    assert (events == expected_events)


@pytest.mark.parametrize("events, offset, expected_locations", [
    (events(), .5, [6.5, 12.5, 18.5, 24.5, 30.5]),
    (events(), -1, [5, 11, 17, 23, 29])
])
def test_offset_events(events, offset, expected_locations):
    events.offset(offset)
    assert events.lget('location') == expected_locations


def test_event_group_list__initializes_non_uniform_inputs_successfully():
    EventGroupList([[1, 2, 3], EventList([1, 2, 3, Event(4, type="beat")])])


@pytest.mark.parametrize("events, expected_event_group_list", [
    (events(), events_grouped_by_type()),
    (EventList([1]), EventGroupList([EventList([1])]))
])
def test_group_by_type(events, expected_event_group_list):
    assert events.group_by_type() == expected_event_group_list


@pytest.mark.parametrize("events, slices, expected_event_groups", [
    (EventList(), [(1, 2)], EventGroupList([[], []])),
    (EventList([1, 2]), [(2, 3)], EventGroupList([[1, 2], []])),
    (EventList([1, 2]), [(0, 8)], EventGroupList([[1, 2]])),
    (EventList([1, 2, 3, 4, 5]), [(1, 3)], EventGroupList([[1], [2, 3], [4, 5]])),
    (EventList([1, 2, 3, 4, 5]), [(0, 3), (3, 4)], EventGroupList([[1, 2, 3], [4], [5]])),
    (EventList([1, 2, 3, 4, 5, 6, 7, 8]), [(1, 3), (5, 7)], EventGroupList([[1], [2, 3], [4, 5], [6, 7], [8]]))
])
def test_group_by_slices(events, slices, expected_event_groups):
    assert events.group_by_slices(slices) == expected_event_groups


def test_event_group_list__group_by_slices_resulting_groups():
    events = EventList([1, 2, 3, 4, 5, 6, 7, 8])
    event_groups = events.group_by_slices([(1, 3), (5, 7)])
    assert event_groups.selected_groups == EventGroupList([[2, 3], [6, 7]])
    assert event_groups.unselected_groups == EventGroupList([[1], [4, 5], [8]])


def test_event_group_list__group_by_types_resulting_groups(events):
    event_groups = events.group_by_type(['silence'])
    assert event_groups.selected_groups == EventGroupList([EventList([Event(6, type='silence')]),
                                                           EventList([Event(30, type='silence')])])
    assert event_groups.unselected_groups == EventGroupList([EventList([Event(12, type='beat'),
                                                                        Event(18, type='beat'),
                                                                        Event(24, type='beat')])])

    # Not specifying type selects all groups
    event_groups = events.group_by_type()
    assert event_groups.selected_groups == event_groups


@pytest.mark.parametrize("event_groups, speeds, offsets, expected_event_groups", [
    (EventGroupList([[1, 2, 3], [4], [5]]), [1 / 2], None, EventGroupList([[1, 3], [4], [5]])),
    (EventGroupList([[1, 2, 3], [4], [5]]), [1 / 2, 1 / 4, 1 / 8], [1], EventGroupList([[2], [4], [5]])),
    (EventGroupList([[1], [2, 3, 4, 5], [4, 5], [6, 7, 8, 9], [8]]), [1, 1 / 2, 2, 1 / 4, 0], None,
     EventGroupList([[1], [2, 4], [4, 4.5, 5], [6], []]))
])
def test_event_group_list__speed_multiply(event_groups, speeds, offsets, expected_event_groups):
    event_groups.speed_multiply(speeds, offsets)
    assert event_groups == expected_event_groups


def test_event_group_list__flatten_yields_event_list():
    assert type(EventGroupList([EventList(), EventList()]).flatten()) == EventList
