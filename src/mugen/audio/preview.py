from enum import Enum
from typing import Optional as Opt, List

import mugen.audio.librosa as librosa
import mugen.utility as util
from mugen.constants import TIME_FORMAT
from mugen.utility import convert_time_list_to_seconds
from mugen.audio.utility import validate_speed_multiplier
from mugen.exceptions import ParameterError


class AudioEvents(str, Enum):
    BEATS = 'beats'
    UNTRIMMED_BEATS = 'beats_untrimmed'
    ONSETS = 'onsets'


@convert_time_list_to_seconds('event_locations')
def preview_event_locations(audio_file: str, event_locations: Opt[List[TIME_FORMAT]], output_path: str, *,
                            event_locations_offset: Opt[float] = None,
                            speed_multiplier: Opt[float] = None,
                            speed_multiplier_offset: Opt[int] = None):
    """
    Generates an audio file with audible bleeps at specified event locations
    
    Args:
        audio_file: audio file to mark
        event_locations: Locations in the audio file to mark for the preview
        output_path: path to save the output .wav file
        
        speed_multiplier: Speeds up or slows down events by grouping them together or splitting them up.
                          Must be of the form x or 1/x, where x is a natural number.
        speed_multiplier_offset: Offsets the grouping of events for slowdown speed_multipliers. 
                                 Takes a max offset of x - 1 for a slowdown of 1/x, where x is a natural number.
    """
    if event_locations_offset:
        event_locations = util.offset_locations(event_locations, event_locations_offset)
    if speed_multiplier is not None:
        event_locations = util.locations_after_speed_multiplier(event_locations, speed_multiplier,
                                                                speed_multiplier_offset)

    librosa.create_marked_audio_file(audio_file, event_locations, output_path)


@validate_speed_multiplier
def preview_audio_event_locations(audio_file: str, output_path: str, method: AudioEvents, **kwargs):
    """
    Generates an audio file with audible bleeps at specified event locations 

    Args:
        audio_file: audio file to mark
        output_path: path to save the output .wav file
        method: Method of generating event locations from the audio file (overruled by event_locations)
                Supported values: See AudioEvents.
        
    See preview_event_locations for other optional parameters
    """
    if method == AudioEvents.BEATS:
        event_locations = librosa.get_beat_locations(audio_file, trim=True)
    elif method == AudioEvents.UNTRIMMED_BEATS:
        event_locations = librosa.get_beat_locations(audio_file, trim=False)
    elif method == AudioEvents.ONSETS:
        event_locations = librosa.get_onset_locations(audio_file)
    else:
        raise ParameterError(f"Invalid AudioEvents value {method}")

    preview_event_locations(audio_file, event_locations, output_path, **kwargs)
