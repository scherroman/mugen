from typing import List, Optional as Opt, Union

import librosa
import soundfile
import numpy as np

from mugen.utility import temp_file_enabled
from mugen.exceptions import ParameterError

MARKED_AUDIO_EXTENSION = '.wav'


@temp_file_enabled('output_path', MARKED_AUDIO_EXTENSION)
def create_marked_audio_file(mark_locations: Union[List[float], np.ndarray], output_path: Opt[str] = None, *,
                             audio_file: Opt[str] = None, duration: float = None):
    if audio_file:
        y, sr = librosa.load(audio_file)
        marked_audio = librosa.core.clicks(times=mark_locations, sr=sr, length=len(y))
        marked_audio = y + marked_audio
    elif duration:
        sr = 22050
        marked_audio = librosa.core.clicks(times=mark_locations, sr=sr, length=int(sr * duration))
    else:
        raise ParameterError("Must provide either audio file or duration.")

    soundfile.write(output_path, marked_audio, sr, 'PCM_24')

    return output_path
