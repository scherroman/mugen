import tkinter as tk
import logging
import os
import sys

from tkinter import filedialog

import mugen.utility as util
from mugen.audio.librosa import MARKED_AUDIO_EXTENSION
from mugen.constants import FileType
from mugen.video.MusicVideo import MusicVideo

""" PATHS """

OUTPUT_PATH_BASE = os.path.join(os.path.dirname(__file__), 'output/')


def audio_preview_path(basedir: str, filename: str) -> str:
    return os.path.join(basedir, filename + "_marked_audio_preview" + MARKED_AUDIO_EXTENSION)


""" COMMAND LINE UTILITY FUNCTIONS """

DEFAULT_MUSIC_VIDEO_NAME = 'music_video'


def get_music_video_name(directory: str, name: str = DEFAULT_MUSIC_VIDEO_NAME):
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
    root.withdraw()
    file = tk.filedialog.askopenfilename(message="Select {} file".format(file_type))
    root.update()

    if file == "":
        print("No {} file was selected.".format(file_type))
        sys.exit(1)

    # # Properly encode file name
    # file = source.encode('utf-8')

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
        files.extend([file.encode('utf-8') for file in source])

    if len(files) == 0:
        print("No {} files were selected.".format(file_type))
        sys.exit(1)

    for file in files:
        logging.debug("{}_file: {}".format(file_type, file))

    return files


def get_files(sources):
    """
    Returns list of file paths from a given list of sources,
    """
    files = []

    for source in sources:
        source_is_dir = os.path.isdir(source)

        # Check if source is file or directory
        if source_is_dir:
            files.extend([file for file in util.listdir_nohidden(source) if os.path.isfile(file)])
        else:
            files.append(source)

    return files


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


def print_rejected_segment_stats(music_video: MusicVideo):
    for trait_filter in music_video.video_segment_filters:
        rejected_segments_for_trait_filter = [segment for segment in music_video.rejected_video_segments if
                                              trait_filter in segment.failed_trait_filters]
        num_failing = len(rejected_segments_for_trait_filter)
        print(f"# rejected segments that failed filter '{trait_filter.trait}': {num_failing}")

