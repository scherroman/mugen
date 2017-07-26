import logging
import os
import sys
import tkinter as tk
from tkinter import filedialog
from typing import List

import mugen.paths as paths
import mugen.utility as util
from mugen import VideoSegment
from mugen.constants import FileType
from mugen.video import MusicVideoGenerator

""" COMMAND LINE UTILITY FUNCTIONS """


def shutdown(error_message: str):
    message(error_message)
    sys.exit(1)


def message(message: str):
    print('\n' + message)


def get_music_video_name(directory: str, basename: str):
    count = 0
    while True:
        music_video_name = basename + f"_{count}"
        music_video_path = os.path.join(directory, music_video_name)

        if not os.path.exists(music_video_path):
            break

        count += 1

    return music_video_name


def prompt_file_selection(file_type: FileType):
    message("Please select a file via the popup dialog.")

    # Select via file selection dialog
    root = tk.Tk()
    root.withdraw()

    file = tk.filedialog.askopenfilename(message=f"Select {file_type} file")
    root.update()

    if file == "":
        shutdown("No {} file was selected.".format(file_type))

    logging.debug("{}_file {}".format(file_type, file))

    return file


def prompt_files_selection(file_type: FileType):
    message("Please select one or more files via the popup dialog.")

    files = []

    # Select files via file selection dialog
    dialog_messsage = "Select {} files".format(file_type)
    while True:
        root = tk.Tk()
        root.withdraw()

        source = tk.filedialog.askopenfilename(message=dialog_messsage, multiple=True)
        dialog_messsage = f"Select more {file_type} files, or press cancel if done"
        root.update()

        if not source:
            break

        # Properly encode file names
        files.append(list(source))

    if len(files) == 0:
        shutdown(f"No {file_type} files were selected.")

    for file in files:
        logging.debug(f"{file_type}_file: {file}")

    return files


def files_from_source(source: str) -> List[str]:
    """
    Parameters
    ----------
    source
        A file source.
        Accepts a file or directory

    Returns
    -------
    A list of all file paths extracted from source
    """
    files = []
    source_is_dir = os.path.isdir(source)

    # Check if source is file or directory
    if source_is_dir:
        files.append([file for file in util.listdir_nohidden(source) if os.path.isfile(file)])
    else:
        files.append(source)

    return files


def files_from_sources(sources: List[str]) -> List[str]:
    """
    Parameters
    ----------
    sources
        A list of file sources.
        Accepts both files and directories

    Returns
    -------
    A list of all file paths extracted from sources
    """
    files = []

    for source in sources:
        files.extend(files_from_source(source))

    return files


def video_files_from_source(source: str) -> List[str]:
    """
    Parameters
    ----------
    source
        A file source.
        Accepts a file or directory

    Returns
    -------
    A list of all video file paths extracted from source
    """
    video_files = []
    source_is_dir = os.path.isdir(source)

    # Check if source is file or directory
    if source_is_dir:
        new_video_files = []
        files = [file for file in util.listdir_nohidden(source) if os.path.isfile(file)]

        for file in files:
            try:
                VideoSegment(file)
            except IOError:
                continue
            else:
                new_video_files.append(file)

        video_files.append(new_video_files)
    else:
        video_files.append(source)

    return video_files


def video_files_from_sources(sources: List[str]) -> List[str]:
    """
    Parameters
    ----------
    sources
        A list of file sources.
        Accepts both files and directories

    Returns
    -------
    A list of all video file paths extracted from sources
    """
    video_files = []

    for source in sources:
        video_files.extend(video_files_from_source(source))

    return video_files


def print_rejected_segment_stats(generator: MusicVideoGenerator):
    message("Filter results:")
    for video_filter in generator.video_filters:
        rejected_segments = [segment for segment in generator.meta[generator.Meta.REJECTED_SEGMENT_STATS]]
        rejected_segments_failed_filter_names = [[failed_filter.name for failed_filter in segment['failed_filters']]
                                                 for segment in rejected_segments]
        num_failing = 0
        for names in rejected_segments_failed_filter_names:
            if video_filter.name in names:
                num_failing += 1

        print(f"{num_failing} segments failed filter '{video_filter.name}'")

