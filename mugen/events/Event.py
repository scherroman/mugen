from typing import Optional

from mugen.constants import TIME_FORMAT
from mugen.utilities.conversion import convert_time_to_seconds


class Event:
    """
    An event which occurs in some time sequence (i.e a song, or music video)
    """

    location: float
    duration: float

    @convert_time_to_seconds(["location", "duration"])
    def __init__(self, location: TIME_FORMAT = None, duration: float = 0):
        """
        Parameters
        ----------
        location
            location of the event in the time sequence (seconds)

        duration
            duration of the event (seconds)
        """
        self.location = location
        self.duration = duration

    def __lt__(self, other):
        return self.location < other.location

    def __repr__(self):
        return self.index_repr()

    def index_repr(self, index: Optional[int] = None):
        if index is None:
            repr_str = f"<{self.__class__.__name__}"
        else:
            repr_str = f"<{self.__class__.__name__} {index}"
        if self.location:
            repr_str += f", location: {self.location:.3f}"
        if self.duration:
            repr_str += f", duration:{self.duration:.3f}"
        repr_str += ">"

        return repr_str

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
