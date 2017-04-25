import sys
from fractions import Fraction
from functools import wraps

from typing import List

from mugen import paths

def validate_speed_multiplier(func):
    """
    Decorator validates speed multiplier and speed_multiplier_offset values
    """

    @wraps(func)
    def _validate_speed_multiplier(*args, **kwargs):
        speed_multiplier = kwargs.get('speed_multiplier')
        speed_multiplier_offset = kwargs.get('speed_multiplier_offset')

        speed_multiplier = Fraction(speed_multiplier).limit_denominator()

        if speed_multiplier:
            if speed_multiplier == 0 or (speed_multiplier.numerator != 1 and speed_multiplier.denominator != 1):
                raise ValueError(f"""Improper speed multiplier {speed_multiplier}. 
                                     Speed multipliers must be of the form x or 1/x, where x is a natural number.""")

        if speed_multiplier_offset:
            if speed_multiplier >= 1:
                raise ValueError(f"""Improper speed multiplier offset {speed_multiplier_offset} for speed multiplier
                                     {speed_multiplier}. Speed multiplier offsets may only be used with slowdown speed
                                     multipliers.""")
            elif speed_multiplier_offset > speed_multiplier.denominator - 1:
                raise ValueError(f"""Improper speed multiplier offset {speed_multiplier_offset} for speed multiplier
                                     {speed_multiplier}. Speed multiplier offset may not be greater than x - 1 for a 
                                     slowdown of 1/x.""")

        func(*args, **kwargs)

    return _validate_speed_multiplier



def create_temp_offset_audio_file(audio_file, offset):
    """
    Create a temporary new audio file with the given offset to use for the music video
    """
    output_path = paths.generate_temp_file_path(paths.file_extension_from_path(audio_file))

    # Generate new temporary audio file with offset
    ffmpeg_cmd = [
        util.get_ffmpeg_binary(),
        '-i', audio_file,
        '-ss', str(offset),
        '-acodec', 'copy',
        output_path
    ]

    try:
        util.execute_ffmpeg_command(ffmpeg_cmd)
    except ex.FFMPEGError as e:
        print(f"Failed to create temporary audio file with specified offset {offset}. Error Code: {e.return_code}, "
              f"Error: {e}")
        raise

    return output_path


def create_temp_marked_audio_file(audio_file, beat_locations):
    output_path = paths.generate_temp_file_path(paths.ESSENTIA_ONSETS_AUDIO_EXTENSION)

    # Load audio
    audio = a_util.load_audio(audio_file)
    onsets_marker = essentia.standard.AudioOnsetsMarker(onsets=beat_locations)
    mono_writer = essentia.standard.MonoWriter(filename=output_path, bitrate=c.DEFAULT_AUDIO_BITRATE)

    # Create preview audio file
    marked_audio = onsets_marker(audio)
    mono_writer(marked_audio)

    return output_path


def preview_audio_beats(audio_file, beat_locations):
    marked_audio_file = create_temp_marked_audio_file(audio_file, beat_locations)
    shutil.move(marked_audio_file, paths.audio_preview_path(audio_file))

