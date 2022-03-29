from enum import Enum

from mugen import MusicVideoGenerator
from mugen.audio.Audio import Audio
from mugen.events.EventGroupList import EventGroupList
from mugen.events.EventList import EventList
from mugen.exceptions import ParameterError
from scripts.cli.utilities import message


class BeatsMode(str, Enum):
    """
    beats: Detect beats
    weak_beats: Detect beats & weak beats
    """

    BEATS = "beats"
    WEAK_BEATS = "weak_beats"


class OnsetsMode(str, Enum):
    """
    onsets: Detect onsets
    backtrack: Shift onset events back to the nearest local minimum of energy
    """

    ONSETS = "onsets"
    BACKTRACK = "backtrack"


class AudioEventsMode(str, Enum):
    """
    Method of generating audio events

    beats: Detect beats
    onsets: Detect onsets
    """

    BEATS = "beats"
    ONSETS = "onsets"


class TargetGroups(str, Enum):
    ALL = "all"
    SELECTED = "selected"
    UNSELECTED = "unselected"


def prepare_events(generator: MusicVideoGenerator, args) -> EventList:
    audio_events_mode = args.audio_events_mode
    event_locations = args.event_locations
    events_offset = args.events_offset

    if audio_events_mode:
        message("Analyzing audio...")
        events = get_events_from_audio(generator.audio, args)
        events, event_groups = apply_moddifiers(events, args)
        message(f"Events:\n{event_groups}")
    elif event_locations:
        events = EventList(event_locations, end=generator.duration)
    else:
        raise ParameterError(
            "Must provide either audio events mode or event locations."
        )

    if events_offset:
        events.offset(events_offset)

    return events


def get_events_from_audio(audio: Audio, args):
    audio_events_mode = args.audio_events_mode
    beats_mode = args.beats_mode
    onsets_mode = args.onsets_mode

    if audio_events_mode == AudioEventsMode.BEATS:
        events = get_beat_events(audio, beats_mode)
    elif audio_events_mode == AudioEventsMode.ONSETS:
        events = get_onset_events(audio, onsets_mode)
    else:
        raise ParameterError(f"Unsupported audio events mode {audio_events_mode}.")

    return events


def get_beat_events(audio: Audio, beats_mode: BeatsMode):
    if beats_mode == BeatsMode.BEATS:
        events = audio.beats()
    elif beats_mode == BeatsMode.WEAK_BEATS:
        events = audio.beats(trim=True)
    else:
        raise ParameterError(f"Unsupported beats mode {beats_mode}.")

    return events


def get_onset_events(audio: Audio, onsets_mode: OnsetsMode):
    if onsets_mode == OnsetsMode.ONSETS:
        events = audio.onsets()
    elif onsets_mode == OnsetsMode.BACKTRACK:
        events = audio.onsets(backtrack=True)
    else:
        raise ParameterError(f"Unsupported onsets mode {onsets_mode}.")

    return events


def apply_moddifiers(events: EventList, args):
    events_speed = args.events_speed
    events_speed_offset = args.events_speed_offset
    group_events_by_slices = args.group_events_by_slices
    group_events_by_type = args.group_events_by_type

    if events_speed:
        events.speed_multiply(events_speed, events_speed_offset)

    if group_events_by_type is not None or group_events_by_slices:
        event_groups = apply_groups(events, args)
        events = event_groups.flatten()
    else:
        event_groups = EventGroupList([events])

    return events, event_groups


def apply_groups(events: EventList, args):
    group_events_by_slices = args.group_events_by_slices
    group_events_by_type = args.group_events_by_type

    if group_events_by_type is not None:
        event_groups = events.group_by_type(select_types=group_events_by_type)
    else:
        event_groups = events.group_by_slices(slices=group_events_by_slices)

    event_groups = apply_group_modifiers(event_groups, args)

    return event_groups


def apply_group_modifiers(event_groups: EventGroupList, args):
    target_groups = args.target_groups
    group_speeds = args.group_speeds
    group_speed_offsets = args.group_speed_offsets

    if target_groups == TargetGroups.ALL:
        event_groups.speed_multiply(group_speeds, group_speed_offsets)
    elif target_groups == TargetGroups.SELECTED:
        event_groups.selected_groups.speed_multiply(group_speeds, group_speed_offsets)
    elif target_groups == TargetGroups.UNSELECTED:
        event_groups.unselected_groups.speed_multiply(group_speeds, group_speed_offsets)
    else:
        raise ParameterError(f"Unknown target groups value {target_groups}.")

    return event_groups
