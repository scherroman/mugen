from mugen.audio.analysis import get_beat_locations, get_onset_locations
from mugen.events import EventList, EventType, EventsMode
from mugen.exceptions import ParameterError


class AudioEventType(EventType):
    END = 'end'
    ONSET = 'onset'
    BEAT = 'beat'
    # SILENCE = 'silence'
    # FADE_IN = 'fade_in'
    # FADE_OUT = 'fade_out'


class AudioEventsMode(EventsMode):
    BEATS = 'beats'
    BEATS_UNTRIMMED = 'beats_untrimmed'
    ONSETS = 'onsets'
    # SMART = 'smart'


def generate_events_from_audio(audio_file: str, event_mode: str) -> EventList:
    """
    Generates events from an audio file
    
    Parameters
    ----------
    audio_file
    
    event_mode
        Method of generating events.
        See :class:`~mugen.audio.constants.AudioEventsMode` for supported values 
    """
    if event_mode == AudioEventsMode.BEATS:
        event_locations = get_beat_locations(audio_file, trim=True)
        event_type = AudioEventType.BEAT
    elif event_mode == AudioEventsMode.BEATS_UNTRIMMED:
        event_locations = get_beat_locations(audio_file, trim=False)
        event_type = AudioEventType.BEAT
    elif event_mode == AudioEventsMode.ONSETS:
        event_locations = get_onset_locations(audio_file)
        event_type = AudioEventType.ONSET
    else:
        raise ParameterError(f"Unsupported event mode {event_mode}")

    events = EventList.from_locations(event_locations, type=event_type)

    return events
