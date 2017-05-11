from typing import List, Optional as Opt, Tuple

import librosa
import numpy as np

from mugen.utility import temp_file_enabled

MARKED_AUDIO_EXTENSION = '.wav'


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




