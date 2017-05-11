from mugen.events import EventType, EventsMode


class VideoEventType(EventType):
    END = 'end'
    CUT = 'cut'
    # CROSSFADE = 'crossfade'
    # CUT_TO_COLOR = 'cut_to_color' ColorEvent(Event)
    # FADE_TO_COLOR = 'fade_to_color' ColorEvent(Event)
    # FADE_FROM_COLOR = 'fade_from_color' ColorEvent(Event)


class VideoEventsMode(EventsMode):
    CUTS = 'cuts'
    # SMART = 'smart'


def event_type_for_mode(event_mode: str) -> EventType:
    if event_mode == VideoEventsMode.CUTS:
        return VideoEventType.CUT
