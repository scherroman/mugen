from mugen.constants import TIME_FORMAT
from mugen.events.Event import Event


class VideoEvent(Event):
    """
    An event in a video
    """

    pass


class Cut(VideoEvent):
    """
    A cut from one piece of sources to another in a video
    """

    def __init__(self, location: TIME_FORMAT, *args, **kwargs):
        super().__init__(location, *args, **kwargs)
