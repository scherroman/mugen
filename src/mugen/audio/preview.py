from typing import Optional as Opt, List

import mugen.audio.utility as a_util
import mugen.audio.events as a_events
from mugen.events import EventList
from mugen.audio.events import AudioEventsMode
from mugen.constants import TIME_FORMAT
from mugen.utility import convert_time_list_to_seconds


def preview_audio_events(audio_file: str, audio_events_mode: AudioEventsMode, output_path: str, *,
                         event_modifiers: Opt[dict] = None):
    """
    Generates an audio file with audible bleeps at generated event locations

    Parameters
    ----------
    audio_file 
        audio file to mark
        
    audio_events_mode 
        Method of generating events from the audio file.
        See :class:`~mugen.audio.constants.AudioEventsMode` for supported values    
        
    output_path 
        path to save the output .wav file
                
    event_modifiers 
        Modifiers to apply to generated events. 
        See :class:`~mugen.events.EventsModifer` for available parameters
    """
    events = a_events.generate_events_from_audio(audio_file, audio_events_mode)
    preview_events(audio_file, events, output_path, event_modifiers=event_modifiers)


@convert_time_list_to_seconds('event_locations')
def preview_event_locations(audio_file: str, event_locations: List[TIME_FORMAT], output_path: str, *,
                            event_modifiers: Opt[dict] = None):
    """
    Generates an audio file with audible bleeps at event locations

    Parameters
    ----------
    audio_file 
        Audio file to overlay bleeps
        
    event_locations 
        Locations in the audio file to mark for the preview
        
    output_path 
        path to save the output .wav file
        
    event_modifiers 
        Modifiers to apply to events. 
        See :class:`~mugen.events.EventsModifer` for available parameters
    """
    events = EventList.from_locations(event_locations)
    preview_events(audio_file, events, output_path, event_modifiers=event_modifiers)


def preview_events(audio_file: str, events: EventList, output_path: str, *, event_modifiers: Opt[dict] = None):
    events.modify(event_modifiers)
    event_locations = [event.location for event in events]

    a_util.create_marked_audio_file(audio_file, event_locations, output_path)



