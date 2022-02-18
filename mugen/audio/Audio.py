from functools import lru_cache
from pathlib import Path
from typing import List

import librosa
import numpy

from mugen.events import Event, EventList


class AudioEvent(Event):
    """
    An event in some audio
    """

    pass


class End(AudioEvent):
    """
    The end of some audio
    """

    pass


class Beat(AudioEvent):
    """
    A beat in some audio
    """

    pass


class WeakBeat(Beat):
    """
    A weak beat in some audio
    """

    pass


class Onset(AudioEvent):
    """
    An onset in some audio
    """

    pass


class Audio:
    """
    Wraps the audio ouput from librosa, providing access to extra features

    Attributes
    ----------
        file
            Loaded audio file

        samples
            Audio samples

        sample_rate
            Audio sample rate

        duration
            Audio duration (seconds)
    """

    file: str
    sample_rate: int
    samples: numpy.ndarray
    duration: float

    def __init__(self, file: str, *, sample_rate: int = 44100):
        """
        Parameters
        ----------
        file
            Audio file to load
        """

        self.file = file
        self.samples, self.sample_rate = librosa.load(file, sr=sample_rate)
        self.duration = librosa.get_duration(filename=self.file)

    def __repr__(self):
        filename = Path(self.file).stem
        return f"<Audio, file: {filename}, duration: {self.duration}>"

    def beats(self, trim: bool = False) -> EventList:
        """
        Gets beat events

        Parameters
        ----------
        trim
            Label weak leading and trailing beats separately

        Returns
        -------
        Detected beat events from the audio
        """
        untrimmed_beats = self._beats()
        untrimmed_beats = EventList(
            [Beat(beat) for beat in untrimmed_beats], end=self.duration
        )

        if not trim:
            beats = untrimmed_beats
        else:
            trimmed_beats = self._beats(trim=True)
            trimmed_leading_beats = [
                beat for beat in untrimmed_beats.locations if beat < trimmed_beats[0]
            ]
            trimmed_trailing_beats = [
                beat for beat in untrimmed_beats.locations if beat > trimmed_beats[-1]
            ]

            # Mark leading & trailing trimmed beats as weak beats
            trimmed_beats = EventList(
                [Beat(beat) for beat in trimmed_beats], end=self.duration
            )
            trimmed_leading_beats = EventList(
                [WeakBeat(beat) for beat in trimmed_leading_beats], end=self.duration
            )
            trimmed_trailing_beats = EventList(
                [WeakBeat(beat) for beat in trimmed_trailing_beats], end=self.duration
            )

            beats = trimmed_leading_beats + trimmed_beats + trimmed_trailing_beats

        return beats

    @lru_cache(maxsize=None)
    def _beats(self, trim: bool = False) -> List[float]:
        """
        Gets beat locations using librosa's beat tracker

        Parameters
        ----------
        trim
            Whether to discard weak beats

        Returns
        -------
        Beat locations
        """
        if trim:
            tempo, beats = librosa.beat.beat_track(
                y=self.samples, sr=self.sample_rate, units="time", trim=True
            )
        else:
            tempo, beats = librosa.beat.beat_track(
                y=self.samples, sr=self.sample_rate, units="time", trim=False
            )

        return beats

    def onsets(self, backtrack: bool = False) -> EventList:
        """
        Gets onset events

        Parameters
        ----------
        backtrack
            Shift onset events back to the nearest local minimum of energy

        Returns
        -------
        Detected onset events from the audio
        """
        if not backtrack:
            onsets = self._onsets()
        else:
            onsets = self._onsets(backtrack=True)

        onsets = EventList([Onset(onset) for onset in onsets], end=self.duration)

        return onsets

    @lru_cache(maxsize=None)
    def _onsets(self, backtrack: bool = False):
        """
        Gets onset locations using librosa's onset detector.

        Parameters
        ----------
        backtrack
            Whether to shift onset events back to the nearest local minimum of energy

        Returns
        -------
        Onset locations
        """
        if backtrack:
            onsets = librosa.beat.onset.onset_detect(
                y=self.samples, sr=self.sample_rate, units="time", backtrack=True
            )
        else:
            onsets = librosa.beat.onset.onset_detect(
                y=self.samples, sr=self.sample_rate, units="time", backtrack=False
            )

        return onsets
