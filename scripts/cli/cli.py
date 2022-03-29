import logging
import sys

from mugen.utilities import system
from scripts.cli.parsing.parsers import parse_arguments, prepare_arguments
from scripts.cli.utilities import message

DEBUG = False


def setup(args):
    global DEBUG
    DEBUG = args.debug
    if DEBUG:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    system.ensure_directory_exists(args.output_directory)


def main():
    # Parse and prepare command
    args = parse_arguments(sys.argv[1:])
    args = prepare_arguments(args)
    setup(args)

    # Run command
    args.func(args)

    message("All Done!")


if __name__ == "__main__":
    main()
