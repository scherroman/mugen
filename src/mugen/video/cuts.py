from mugen.constants import TIME_FORMAT
from mugen.video.events import VideoEvent


class Cut(VideoEvent):
    """
    A cut from one piece of sources to another in a video
    """

    def __init__(self, location: TIME_FORMAT, *args, **kwargs):
        super().__init__(location, *args, **kwargs)

