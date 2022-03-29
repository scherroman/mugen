import argparse

from scripts.cli.commands import create_music_video, preview_music_video


def add_create_parser(command_parsers, parents):
    create_parser = command_parsers.add_parser(
        "create",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Create a new music video",
    )
    create_parser.set_defaults(func=create_music_video)
    create_parser.add_argument(
        "-v",
        "--video-sources",
        dest="video_sources",
        nargs="+",
        required=True,
        help="""The video sources for the music video.
         Takes a list of files and folders separated by spaces.
         Supports passing globs to target one or more files or folders.
         (e.g.) Miyazaki/* to use a folder containing multiple miyazaki movies or subfolders with miyazaki movies.
         Supports any video format supported by ffmpeg,
         such as .ogv, .mp4, .mpeg, .avi, .mov, etc...""",
    )
    create_parser.add_argument(
        "-vw",
        "--video-source-weights",
        dest="video_source_weights",
        type=float,
        nargs="+",
        default=[],
        help="""Weights for controlling how often each video source should be used
         in the music video. Takes a list of numbers separated by spaces.
         (i.e.) Pass --weights .6 .4 or --weights 6 4 to use the first video source
         (a series of 26 episodes) 60%% of the time, and the second video source
         (a movie) 40%% of the time""",
    )
    create_parser.add_argument(
        "-fi",
        "--fade-in",
        dest="fade_in",
        type=float,
        help="Fade-in for the music video (seconds)",
    )
    create_parser.add_argument(
        "-fo",
        "--fade-out",
        dest="fade_out",
        type=float,
        help="Fade-out for the music video (seconds)",
    )

    return create_parser


def add_preview_parser(command_parsers, parents):
    preview_parser = command_parsers.add_parser(
        "preview",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Create a quick preview of your music video by marking cut locations with beeps and flashes",
    )
    preview_parser.set_defaults(func=preview_music_video)

    return preview_parser
