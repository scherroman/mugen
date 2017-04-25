from enum import Enum
from typing import Optional as Opt, List, Tuple

import librosa
import numpy as np

from mugen.utility import temp_file_enabled


MARKED_AUDIO_EXTENSION = '.wav'


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


@temp_file_enabled('output_path', MARKED_AUDIO_EXTENSION)
def create_marked_audio_file(audio_file: str, mark_locations: List[float], output_path: Opt[str] = None):
    marked_audio, sr = _get_marked_audio(audio_file, mark_locations)
    librosa.output.write_wav(path=output_path, y=marked_audio, sr=sr)

    return output_path


def _get_marked_audio(audio_file: str, mark_locations: List[float]) -> Tuple[np.ndarray, int]:
    y, sr = librosa.load(audio_file)
    clicks = librosa.core.clicks(times=mark_locations, sr=sr, length=len(y))
    marked_audio = y + clicks

    return marked_audio, sr

