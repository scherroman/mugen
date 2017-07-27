import pytest

from mugen.events import Event, EventList, EventGroupList


class Beat(Event):
    pass


class Silence(Event):
    pass


@pytest.fixture
def events() -> EventList:
    return EventList([Silence(6),
                      Beat(12),
                      Beat(18),
                      Beat(24),
                      Silence(30)])


@pytest.fixture
def events_grouped_by_type() -> EventGroupList:
    return EventGroupList([EventList([Silence(6)]),
                           EventList([Beat(12), Beat(18), Beat(24)]),
                           EventList([Silence(30)])])


@pytest.fixture
def events_speed_multiplied_2x() -> EventList:
    return EventList([Silence(6),
                      Beat(12), Beat(15),
                      Beat(18), Beat(21),
                      Beat(24),
                      Silence(30)])


@pytest.fixture
def events_speed_multiplied_1_2x() -> EventList:
    return EventList([Silence(6),
                      Beat(12),
                      Beat(24),
                      Silence(30)])


@pytest.fixture
def events_speed_multiplied_1_2x_offset_1() -> EventList:
    return EventList([Silence(6),
                      Beat(18),
                      Silence(30)])


@pytest.fixture
def events_speed_multiplied_1_3x() -> EventList:
    return EventList([Silence(6),
                      Beat(12),
                      Silence(30)])


def test_event_list__initializes_non_uniform_inputs_successfully():
    EventList([1, 2, 3, Beat(4)])


@pytest.mark.parametrize("events, speed, offset, expected_events", [
    (EventList([]), 5, None, EventList([])),
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


@pytest.mark.parametrize("events, events_b, expected_events", [
    (EventList([10, 20, 30]), EventList([5, 15, 25, 35]), EventList([5, 10, 15, 20, 25, 30, 35]))
])
def test_add_events(events, events_b, expected_events):
    events.add_events(events_b)
    assert events == expected_events


@pytest.mark.parametrize("events_a, events_b, expected_events", [
    (EventList([6, 12], end=30), EventList([18, 24], end=30), EventList([6, 12, 18, 24], end=30)),
    (EventList([6, 12], end=18), EventList([18, 24], end=30), EventList([6, 12, 18, 24], end=30))
])
def test_event_list_concatenate(events_a, events_b, expected_events):
    assert events_a + events_b == expected_events


def test_event_group_list__initializes_non_uniform_inputs_successfully():
    EventGroupList([[1, 2, 3], EventList([1, 2, 3, Beat(4)])])


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
    event_groups = events.group_by_type(['Silence'])
    assert event_groups.selected_groups == EventGroupList([EventList([Silence(6)]),
                                                          EventList([Silence(30)])])
    assert event_groups.unselected_groups == EventGroupList([EventList([Beat(12),
                                                                       Beat(18),
                                                                       Beat(24)])])

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


def test_event_group_list__flatten():
    assert EventGroupList([EventList([1, 2, 3], end=50), EventList([4, 5, 6], end=50)]).flatten() == \
           EventList([1, 2, 3, 4, 5, 6], end=50)
