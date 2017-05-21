from fractions import Fraction
from typing import Optional as Opt, List
import tkinter as tk
import logging
import os
import sys

from tkinter import filedialog

import mugen.paths as paths
import mugen.utility as util
from mugen import VideoSegment
from mugen.constants import FileType
from mugen.mixins.Weightable import Weightable
from mugen.video import MusicVideoGenerator
from mugen.video.MusicVideo import MusicVideo

import bin.constants as cli_c

""" COMMAND LINE UTILITY FUNCTIONS """


def get_music_video_name(directory: str, name: Opt[str] = None):
    if not name:
        name = cli_c.DEFAULT_MUSIC_VIDEO_NAME

    count = 0
    while True:
        music_video_name = name + "_%s" % count
        music_video_path = os.path.join(directory, music_video_name)

        if not os.path.exists(music_video_path):
            break

        count += 1

    return music_video_name


def prompt_file_selection(file_type: FileType):
    # Select via file selection dialog
    root = tk.Tk()
    root.lift()
    root.withdraw()
    file = tk.filedialog.askopenfilename(message="Select {} file".format(file_type))
    root.update()

    if file == "":
        print("No {} file was selected.".format(file_type))
        sys.exit(1)

    logging.debug("{}_file {}".format(file_type, file))

    return file


def prompt_files_selection(file_type: FileType):
    files = []

    # Select files via file selection dialog
    message = "Select {} files".format(file_type)
    while True:
        root = tk.Tk()
        root.withdraw()

        source = tk.filedialog.askopenfilename(message=message, multiple=True)
        message = "Select more {} files, or press cancel if done".format(file_type)
        root.update()

        if not source:
            break

        # Properly encode file names
        files.append(list(source))

    if len(files) == 0:
        print("No {} files were selected.".format(file_type))
        sys.exit(1)

    for file in files:
        logging.debug("{}_file: {}".format(file_type, file))

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


def validate_path(*paths):
    for path in paths:
        if path and not os.path.exists(path):
            print("Path {} does not exist.".format(path))
            sys.exit(1)


def validate_replace_segments(replace_segments, video_segments):
    for segment in replace_segments:
        if segment < 0 or segment > (len(video_segments) - 1):
            print("No segment {} exists in spec for music video".format(segment))
            sys.exit(1)


def print_weight_stats(music_video_generator: MusicVideoGenerator):
    print("\nVideo Source Weights:")
    for video_segment, weight in zip(music_video_generator.video_sources,
                                     music_video_generator.video_sources.weight_percentages):
        print(f"{paths.filename_from_path(video_segment.filename)}: {weight}%")


def print_rejected_segment_stats(music_video: MusicVideo):
    print("\nFilter results:")
    for video_filter in music_video.video_filters:
        rejected_segments_for_video_filter = [segment for segment in music_video.rejected_video_segments if
                                              video_filter in segment.failed_filters]
        num_failing = len(rejected_segments_for_video_filter)
        print(f"{num_failing} segments failed filter '{video_filter.name}'")

