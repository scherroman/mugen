from enum import Enum

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


class TrimMode(str, Enum):
    """
    trim: Remove weak beats
    trim_lead: Remove leading weak beats
    trim_trail: Remove trailing weak beats
    """
    NONE = 'none'
    TRIM = 'trim'
    TRIM_LEAD = 'trim_lead'
    TRIM_TRAIL = 'trim_trail'


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

    def beats(self, mode: str = BeatsMode.BEATS, *, trim_mode: str = TrimMode.NONE) -> EventList:
        """
        Gets beats using librosa's beat tracker.
        
        Parameters
        ----------
        mode
            Method of generating beats from the audio
            See :class:`~mugen.audio.Audio.BeatsMode` for supported values.

        trim_mode
            Method of trimming (removing) weak beat events
            See :class:`~mugen.audio.Audio.TrimMode` for supported values.
        Returns
        -------
        Detected beats from the audio
        """
        # Mark leading & trailing trimmed beats as weak beats
        tempo, trimmed_beats = librosa.beat.beat_track(y=self.samples, sr=self.sample_rate, units='time',
                                                       trim=True)
        tempo, untrimmed_beats = librosa.beat.beat_track(y=self.samples, sr=self.sample_rate, units='time',
                                                         trim=False)
        trimmed_leading_beats = [beat for beat in untrimmed_beats if beat < trimmed_beats[0]]
        trimmed_trailing_beats = [beat for beat in untrimmed_beats if beat > trimmed_beats[-1]]

        untrimmed_beats = EventList([Event(beat, type=AudioEventType.BEAT) for beat in untrimmed_beats])
        trimmed_beats = EventList([Event(beat, type=AudioEventType.BEAT) for beat in trimmed_beats])
        trimmed_leading_beats = EventList([Event(beat, type=AudioEventType.WEAK_BEAT) for beat in
                                           trimmed_leading_beats])
        trimmed_trailing_beats = EventList([Event(beat, type=AudioEventType.WEAK_BEAT) for beat in
                                            trimmed_trailing_beats])

        if mode == BeatsMode.BEATS:
            beats = untrimmed_beats
        elif mode == BeatsMode.WEAK_BEATS:
            if trim_mode == TrimMode.NONE:
                beats = trimmed_leading_beats + trimmed_beats + trimmed_trailing_beats
            elif trim_mode == TrimMode.TRIM:
                beats = trimmed_beats
            elif trim_mode == TrimMode.TRIM_LEAD:
                beats = trimmed_beats + trimmed_trailing_beats
            elif trim_mode == TrimMode.TRIM_TRAIL:
                beats = trimmed_leading_beats + trimmed_beats
            else:
                raise ParameterError(f"Unsupported trim mode {trim_mode}.")
        else:
            raise ParameterError(f"Unsupported beats mode {mode}.")

        return beats

    def onsets(self, mode: str = OnsetsMode.ONSETS) -> EventList:
        """
        Gets onsets using librosa's onset detector.
        
        Parameters
        ----------
        mode
            Method of generating onsets from the audio
            See :class:`~mugen.audio.Audio.OnsetsMode` for supported values.

        Returns
        -------
        Detected onsets from the audio
        """
        if mode == OnsetsMode.ONSETS:
            onsets = librosa.beat.onset.onset_detect(y=self.samples, sr=self.sample_rate, units='time')
            onsets = EventList([Event(onset, type=AudioEventType.ONSET) for onset in onsets])
        elif mode == OnsetsMode.BACKTRACK:
            onsets = librosa.beat.onset.onset_detect(y=self.samples, sr=self.sample_rate, units='time', backtrack=True)
            onsets = EventList([Event(onset, type=AudioEventType.ONSET_BACKTRACKED) for onset in onsets])
        else:
            raise ParameterError(f"Unsupported onsets mode {mode}.")

        return onsets
