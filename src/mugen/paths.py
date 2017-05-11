import os
import tempfile


TEMP_PATH_BASE = tempfile.TemporaryDirectory().name


def generate_temp_file_path(extension: str) -> str:
    return TEMP_PATH_BASE + next(tempfile._RandomNameSequence()) + extension


def filename_and_extension_from_path(path: str) -> (str, str):
    """
    Returns
    -------
    The path's filename and extension
    """
    basename = os.path.basename(path)
    return os.path.splitext(basename)


def filename_from_path(path: str) -> str:
    """
    Returns
    -------
    The path's filename minus its extension
    """
    return filename_and_extension_from_path(path)[0]


def file_extension_from_path(path: str) -> str:
    """
    Returns
    -------
    The path's file extension
    """
    return filename_and_extension_from_path(path)[1] or ""
