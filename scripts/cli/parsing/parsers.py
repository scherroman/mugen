import argparse
import os
import re
import sys
from pathlib import Path

from mugen.exceptions import ParameterError
from scripts.cli.parsing.commands import add_create_parser, add_preview_parser
from scripts.cli.parsing.shared import (
    get_audio_parser,
    get_event_parser,
    get_video_parser,
)


def prepare_arguments(args):
    """
    Formats and validates program inputs
    """
    if (
        get_attribute(args, "duration") is not None
        and get_attribute(args, "event_locations") is None
    ):
        raise ParameterError("--duration option requires --event-locations.")

    if get_attribute(args, "video_dimensions") is not None:
        args.video_dimensions = tuple(args.video_dimensions)

    return args


def slice(arg):
    """
    Custom slice type for argparse
    """
    expr = r"\(?(\d+),(\d+)\)?"
    try:
        finds = re.findall(expr, arg)
        x, y = map(int, finds[0])
    except IndexError:
        raise argparse.ArgumentTypeError(
            f"Improper slice {arg}. Slices must be numbers of the form x,y or (x,y)"
        )
    else:
        return x, y


def get_attribute(*args, **kwargs):
    return getattr(*args, None, **kwargs)


class HelpParser(argparse.ArgumentParser):
    """
    Custom Parser which prints help on error
    """

    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help()
        sys.exit(2)


def parse_arguments(args):

    parser = get_help_parser(args)
    command_parsers = parser.add_subparsers()

    # Shared parameters
    event_parser = get_event_parser()
    video_parser = get_video_parser()
    audio_parser = get_audio_parser()

    # Commands
    add_create_parser(command_parsers, [audio_parser, video_parser, event_parser])
    add_preview_parser(command_parsers, [audio_parser, event_parser])

    # Exit if no arguments are passed in
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args(args)


def get_help_parser(args):
    help_parser = HelpParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    help_parser.add_argument(
        "-db",
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Pass in this argument to print useful debug info",
    )
    help_parser.add_argument(
        "-od",
        "--output-directory",
        dest="output_directory",
        default=os.path.join(Path.home(), "Desktop"),
        help="The directory in which to store any output from this application. Will create the directory if non-existent",
    )

    return help_parser
