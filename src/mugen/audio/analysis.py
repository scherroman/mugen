from typing import List

import librosa


def get_audio_duration(audio_file) -> float:
    y, sr = librosa.load(audio_file)
    duration = librosa.core.get_duration(y=y, sr=sr)

    return duration


def get_beat_locations(audio_file: str, trim: bool = True) -> List[float]:
    y, sr = librosa.load(audio_file)
    tempo, beat_locations = librosa.beat.beat_track(y=y, sr=sr, units='time', trim=trim)
    beat_locations.tolist()

    return beat_locations


def get_onset_locations(audio_file: str) -> List[float]:
    y, sr = librosa.load(audio_file)
    onset_locations = librosa.beat.onset.onset_detect(y=y, sr=sr, units='time')
    onset_locations.tolist()

    return onset_locations


