from enum import Enum
from functools import lru_cache
from typing import List

import librosa
import numpy as np

from mugen import paths
from mugen.events import EventList, Event, EventsMode, EventType
from mugen.exceptions import ParameterError


class AudioEventType(EventType):
    END = 'end'
    BEAT = 'beat'
    WEAK_BEAT = 'weak_beat'
    ONSET = 'onset'
    ONSET_BACKTRACKED = 'onset_backtracked'
    # SILENCE
    # FADE_IN
    # FADE_OUT
    # DROP


class AudioEventsMode(EventsMode):
    """
    beats: Detect beats
    weak_beats: Detect onsets
    """
    BEATS = 'beats'
    ONSETS = 'onsets'


class BeatsMode(str, Enum):
    """
    beats: Detect beats
    weak_beats: Detect beats & weak beats
    """
    BEATS = 'beats'
    WEAK_BEATS = 'weak_beats'


class OnsetsMode(str, Enum):
    """
    onsets: Detect onsets
    backtrack: Shift onset events back to the nearest local minimum of energy
    """
    ONSETS = 'onsets'
    BACKTRACK = 'backtrack'


class Audio:
    """
    Wraps the audio ouput from librosa, providing access to extra features
    
    Attributes
    ----------
        audio_file
            Loaded audio file
            
        samples
            Audio samples
        
        sample_rate
            Audio sample rate
                        
        duration
            Audio duration (seconds)
    """
    audio_file: str
    sample_rate: int
    samples: np.ndarray
    duration: float

    def __init__(self, audio_file: str, *, sample_rate: int = 44100):
        """        
        Parameters
        ----------
        audio_file
            Audio file to load
        """

        self.audio_file = audio_file
        self.samples, self.sample_rate = librosa.load(audio_file, sr=sample_rate)
        self.duration = librosa.get_duration(y=self.samples, sr=self.sample_rate)

    def __repr__(self):
        filename = paths.filename_from_path(self.audio_file)
        return f'<Audio, file: {filename}, duration: {self.duration}>'

    def beats(self, mode: str = BeatsMode.BEATS) -> EventList:
        """
        Gets beat events
        
        Parameters
        ----------
        mode
            Method of generating beats from the audio
            See :class:`~mugen.audio.Audio.BeatsMode` for supported values.

        Returns
        -------
        Detected beat events from the audio
        """
        untrimmed_beats = self._beats()
        untrimmed_beats = EventList([Event(beat, type=AudioEventType.BEAT) for beat in untrimmed_beats])

        if mode == BeatsMode.BEATS:
            beats = untrimmed_beats
        elif mode == BeatsMode.WEAK_BEATS:
            trimmed_beats = self._beats(trim=True)
            trimmed_leading_beats = [beat for beat in untrimmed_beats.locations if beat < trimmed_beats[0]]
            trimmed_trailing_beats = [beat for beat in untrimmed_beats.locations if beat > trimmed_beats[-1]]

            # Mark leading & trailing trimmed beats as weak beats
            trimmed_beats = EventList([Event(beat, type=AudioEventType.BEAT) for beat in trimmed_beats])
            trimmed_leading_beats = EventList([Event(beat, type=AudioEventType.WEAK_BEAT) for beat in
                                               trimmed_leading_beats])
            trimmed_trailing_beats = EventList([Event(beat, type=AudioEventType.WEAK_BEAT) for beat in
                                                trimmed_trailing_beats])

            beats = trimmed_leading_beats + trimmed_beats + trimmed_trailing_beats
        else:
            raise ParameterError(f"Unsupported beats mode {mode}.")

        return beats

    @lru_cache(maxsize=None)
    def _beats(self, trim=False) -> List[float]:
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
            tempo, beats = librosa.beat.beat_track(y=self.samples, sr=self.sample_rate, units='time',
                                                   trim=True)
        else:
            tempo, beats = librosa.beat.beat_track(y=self.samples, sr=self.sample_rate, units='time',
                                                   trim=False)

        return beats

    def onsets(self, mode: str = OnsetsMode.ONSETS) -> EventList:
        """
        Gets onset events
        
        Parameters
        ----------
        mode
            Method of generating onsets from the audio
            See :class:`~mugen.audio.Audio.OnsetsMode` for supported values.

        Returns
        -------
        Detected onset events from the audio
        """
        if mode == OnsetsMode.ONSETS:
            onsets = self._onsets()
            onsets = EventList([Event(onset, type=AudioEventType.ONSET) for onset in onsets])
        elif mode == OnsetsMode.BACKTRACK:
            onsets = self._onsets(backtrack=True)
            onsets = EventList([Event(onset, type=AudioEventType.ONSET_BACKTRACKED) for onset in onsets])
        else:
            raise ParameterError(f"Unsupported onsets mode {mode}.")

        return onsets

    @lru_cache(maxsize=None)
    def _onsets(self, backtrack=False):
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
            onsets = librosa.beat.onset.onset_detect(y=self.samples, sr=self.sample_rate, units='time', backtrack=True)
        else:
            onsets = librosa.beat.onset.onset_detect(y=self.samples, sr=self.sample_rate, units='time', backtrack=False)

        return onsets
