from typing import Optional as Opt, List

from mugen.events import EventType, EventsMode, EventList, Event


class VideoEventType(EventType):
    END = 'end'
    CUT = 'cut'
    # COLOR = 'color'
    # CROSS_FADE = 'cross_fade'
    # FADE_OUT
    # FADE_IN
    # CROSS_CUT
    # JUMP_CUT


class VideoEventsMode(EventsMode):
    CUTS = 'cuts'
    # SMART_CUTS
    # SMART_FX_CUTS


class VideoEventList(EventList):
    """
    A list of video events with extended functionality
    """

    def __init__(self, video_cuts: Opt[List[Event]] = None):
        if video_cuts is None:
            video_cuts = []

        super().__init__(video_cuts)

    def ensure_end_event(self, location: float):
        """
        Adds the END event to the list of video events.
        """
        if self and self[-1].type == VideoEventType.END:
            return

        self.append(Event(location, type=VideoEventType.END))

    @classmethod
    def from_audio_events(cls, audio_events: EventList, video_events_mode: str) -> 'VideoEventList':
        video_cuts = VideoEventList()

        # Convert audio_events to video events
        for event in audio_events:
            next_video_cuts = cls.from_audio_event(event, video_events_mode)
            video_cuts.extend(next_video_cuts)

        return video_cuts

    @classmethod
    def from_audio_event(cls, audio_event: Event, video_events_mode: str) -> 'VideoEventList':
        video_cuts = VideoEventList()

        # Convert audio_event to video events
        if video_events_mode == VideoEventsMode.CUTS:
            video_cut = Event(audio_event.location, type=VideoEventType.CUT)
            video_cuts.append(video_cut)

        return video_cuts
