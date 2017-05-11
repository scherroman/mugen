import pytest

from mugen.events import Event, EventList


@pytest.fixture
def events() -> EventList:
    return EventList([Event(6, type='silence'),
                      Event(12, type='beat'),
                      Event(18, type='beat'),
                      Event(20, type='beat'),
                      Event(30, type='silence')])


@pytest.fixture
def events_speed_multiplied_2x() -> EventList:
    return EventList([Event(6, type='silence'), Event(9, type='silence'),
                      Event(12, type='beat'), Event(15, type='beat'),
                      Event(18, type='beat'), Event(19, type='beat'),
                      Event(20, type='beat'), Event(25, type='beat'),
                      Event(30, type='silence')])


@pytest.fixture
def events_speed_multiplied_1_2x() -> EventList:
    return EventList([Event(6, type='silence'),
                      Event(18, type='beat'),
                      Event(30, type='silence')])


@pytest.fixture
def events_speed_multiplied_1_2x_offset_1() -> EventList:
    return EventList([Event(12, type='beat'),
                      Event(20, type='beat')])

@pytest.fixture
def events_speed_multiplied_1_3x() -> EventList:
    return EventList([Event(6, type='silence'),
                      Event(20, type='beat')])


@pytest.mark.parametrize("events, speed_multiplier, speed_multiplier_offset, expected_events", [
    (EventList([]), 5, 0, []),
    (EventList([Event(6)]), 3, 0, EventList([Event(6)])),
    (EventList([Event(6), Event(12)]), 1 / 3, 0, EventList([Event(6)])),
    (events(), 1, None, events()),
    (events(), 1 / 2, None, events_speed_multiplied_1_2x()),
    (events(), 1 / 2, 1, events_speed_multiplied_1_2x_offset_1()),
    (events(), 1 / 3, 0, events_speed_multiplied_1_3x()),
    (events(), 2, None, events_speed_multiplied_2x())
])
def test_speed_multiply_events(events, speed_multiplier, speed_multiplier_offset, expected_events):
    events.speed_multiply(speed_multiplier, speed_multiplier_offset)
    assert (events == expected_events)


@pytest.mark.parametrize("events, offset, expected_locations", [
    (events(), .5, [6.5, 12.5, 18.5, 20.5, 30.5]),
    (events(), -1, [5, 11, 17, 19, 29])
])
def test_offset_events(events, offset, expected_locations):
    events.offset(offset)
    assert events.locations == expected_locations
