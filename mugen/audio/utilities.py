from typing import List, Optional, Union

import librosa
import numpy
import soundfile

from mugen.utilities.system import use_temporary_file_fallback

DEFAULT_SUBTYPE = "PCM_24"
DEFAULT_SAMPLE_RATE = 22050
MARKED_AUDIO_EXTENSION = ".wav"


@use_temporary_file_fallback("output_path", MARKED_AUDIO_EXTENSION)
def mark_audio_file(
    audio_file: str,
    marks: Union[List[float], numpy.ndarray],
    output_path: Optional[str] = None,
):
    """
    Creates a new audio file with audible bleeps at event locations

    Parameters
    ----------
    audio_file
        Audio file to mark

    marks
        Locations to mark the audio file

    output_path
        Path to save the output file
    """
    audio, sample_rate = librosa.load(audio_file)
    marks = librosa.core.clicks(times=marks, sr=sample_rate, length=len(audio))
    marked_audio = audio + marks
    soundfile.write(output_path, marked_audio, sample_rate, DEFAULT_SUBTYPE)

    return output_path


@use_temporary_file_fallback("output_path", MARKED_AUDIO_EXTENSION)
def create_marked_audio_file(
    marks: Union[List[float], numpy.ndarray],
    duration: float,
    output_path: Optional[str] = None,
):
    sample_rate = DEFAULT_SAMPLE_RATE
    marked_audio = librosa.core.clicks(
        times=marks, sr=sample_rate, length=int(sample_rate * duration)
    )
    soundfile.write(output_path, marked_audio, sample_rate, DEFAULT_SUBTYPE)

    return output_path
