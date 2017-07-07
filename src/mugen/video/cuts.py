from typing import Optional as Opt, List, Union

from moviepy.video.VideoClip import VideoClip

import mugen.video.effects as v_effects
from mugen.constants import TIME_FORMAT
from mugen.events import EventList
from mugen.video.effects import VideoEffect
from mugen.video.events import VideoEvent


class Cut(VideoEvent):
    """
    A cut from one piece of content to another in a video
    """

    def __init__(self, location: TIME_FORMAT, *args, **kwargs):
        super().__init__(location, *args, **kwargs)


class EndCut(Cut):
    """
    The end of a video
    """
    pass


class CutList(EventList):
    """
    A list of cuts with extended functionality
    """

    def __init__(self, cuts: Opt[List[Union[Cut, TIME_FORMAT]]] = None):
        if cuts is None:
            cuts = []

        for index, cut in enumerate(cuts):
            if not isinstance(cut, Cut):
                # Convert video_cut location to VideoCut
                cuts[index] = Cut(cut)

        super().__init__(cuts)

    def ensure_end_cut(self, location: TIME_FORMAT):
        """
        Adds the ending cut to the list of cuts.
        """
        if self and isinstance(self[-1], EndCut):
            return

        self.append(EndCut(location))

    @classmethod
    def from_events(cls, events: EventList) -> 'CutList':
        """
        Creates a list of cuts from a list of events

        Parameters
        ----------
        events
            events to convert into cuts
        """
        return CutList([Cut(event.location) for event in events])
