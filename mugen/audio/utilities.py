from typing import List, Optional, Union

import numpy
import librosa
import soundfile

from mugen.exceptions import ParameterError
from mugen.utilities import temp_file_enabled

MARKED_AUDIO_EXTENSION = '.wav'


@temp_file_enabled('output_path', MARKED_AUDIO_EXTENSION)
def create_marked_audio_file(mark_locations: Union[List[float], numpy.ndarray], output_path: Optional[str] = None, *,
                             audio_file: Optional[str] = None, duration: float = None):
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
