import os
import tempfile

TEMP_PATH_BASE = tempfile.TemporaryDirectory().name

OUTPUT_PATH_BASE = 'output/'
VIDEO_OUTPUT_EXTENSION = '.mkv'
SUBTITLES_EXTENSION = '.srt'
SPEC_EXTENSION = '.json'
ESSENTIA_ONSETS_AUDIO_EXTENSION = '.wav'

SEGMENTS_DIRECTORY = 'video_segments/'
SR_DIRECTORY = 'video_segment_rejects/'


def segments_dir(basedir: str) -> str:
    return basedir + SEGMENTS_DIRECTORY + '/'


def sr_dir(basedir: str) -> str:
    return basedir + SR_DIRECTORY + '/'


def trait_filter_dir(trait_filter: str, basedir: str) -> str:
    return sr_dir(basedir) + trait_filter + '/'


def video_file_output_path(filename: str, basedir: str) -> str:
    return basedir + filename + VIDEO_OUTPUT_EXTENSION


def spec_output_path(basedir: str) -> str:
    return basedir + 'spec' + SPEC_EXTENSION


def audio_preview_path(basedir: str) -> str:
    return basedir + "marked_audio_preview" + ESSENTIA_ONSETS_AUDIO_EXTENSION


def generate_temp_file_path(extension: str) -> str:
    return TEMP_PATH_BASE + next(tempfile._RandomNameSequence()) + extension


def filename_and_extension_from_path(path: str) -> (str, str):
    """
    Returns: path's filename and extension
    """
    basename = os.path.basename(path)
    return os.path.splitext(basename)


def filename_from_path(path: str) -> str:
    """
    Returns: path's filename without its extension
    """
    return file_extension_from_path(path)[0]


def file_extension_from_path(path: str) -> str:
    """
    Returns: path's file extension
    """
    return file_extension_from_path(path)[1] or ""