import os
import tempfile

import mugen.video.constants as vc

TEMP_PATH_BASE = tempfile.TemporaryDirectory().name


def trait_filter_dir(trait_filter: str, basedir: str) -> str:
    return os.path.join(basedir, trait_filter)


def spec_output_path(basedir: str) -> str:
    return os.path.join(basedir, 'spec' + vc.SPEC_EXTENSION)


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
    return filename_and_extension_from_path(path)[0]


def file_extension_from_path(path: str) -> str:
    """
    Returns: path's file extension
    """
    return filename_and_extension_from_path(path)[1] or ""
