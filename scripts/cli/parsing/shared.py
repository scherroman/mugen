import argparse
from fractions import Fraction

from mugen import VideoFilter
from mugen.video.filters import DEFAULT_VIDEO_FILTERS
from mugen.video.io.VideoWriter import VideoWriter
from scripts.cli.events import AudioEventsMode, BeatsMode, OnsetsMode, TargetGroups

DEFAULT_MUSIC_VIDEO_NAME = "music_video"


def get_audio_parser():
    audio_parser = argparse.ArgumentParser(add_help=False)

    audio_parser.add_argument(
        "-a",
        "--audio-source",
        dest="audio_source",
        required=True,
        help="The audio file for the music video. Supports any audio format supported by ffmpeg, such as wav, aiff, flac, ogg, mp3, etc...",
    )
    audio_parser.add_argument(
        "-uoa",
        "--use-original-audio",
        dest="use_original_audio",
        action="store_true",
        default=False,
        help="Whether or not to use the original audio from the video segments for the music video",
    )

    audio_parser.add_argument(
        "-aem",
        "--audio-events-mode",
        dest="audio_events_mode",
        default=AudioEventsMode.BEATS,
        help=f"Method of generating events from the audio file. Supported values are {[e.value for e in AudioEventsMode]}",
    )
    audio_parser.add_argument(
        "-bm",
        "--beats-mode",
        dest="beats_mode",
        default=BeatsMode.BEATS,
        help=f"Method of generating beat events from the audio file. Supported values are {[e.value for e in BeatsMode]}",
    )
    audio_parser.add_argument(
        "-om",
        "--onsets-mode",
        dest="onsets_mode",
        default=OnsetsMode.ONSETS,
        help=f"Method of generating onset events from the audio file. Supported values are {[e.value for e in OnsetsMode]}",
    )

    audio_parser.add_argument(
        "-ac",
        "--audio-codec",
        dest="audio_codec",
        default=VideoWriter.DEFAULT_AUDIO_CODEC,
        help="The audio codec for the music video if --use-original-audio is enabled. Supports any codec supported by moviepy.",
    )
    audio_parser.add_argument(
        "-ab",
        "--audio-bitrate",
        dest="audio_bitrate",
        type=int,
        default=VideoWriter.DEFAULT_AUDIO_BITRATE,
        help="The audio bitrate (kbps) for the music video if --use-original-audio is enabled",
    )

    return audio_parser


def get_video_parser():
    video_parser = argparse.ArgumentParser(add_help=False)

    video_parser.add_argument(
        "-vn",
        "--video-name",
        dest="video_name",
        default=DEFAULT_MUSIC_VIDEO_NAME,
        help="The name for the music video. On subsequent runs, the program will output <music_video_name>_0, <music_video_name>_1, etc...",
    )

    video_parser.add_argument(
        "-vf",
        "--video-filters",
        dest="video_filters",
        nargs="+",
        default=DEFAULT_VIDEO_FILTERS,
        help=f"Video filters that each segment in the music video must pass. Supported values are {[filter.name for filter in VideoFilter]}",
    )
    video_parser.add_argument(
        "-evf",
        "--exclude-video-filters",
        dest="exclude_video_filters",
        nargs="+",
        help="Video filters to exclude from the default video filters. See video_filters for supported values",
    )
    video_parser.add_argument(
        "-ivf",
        "--include-video-filters",
        dest="include_video_filters",
        nargs="+",
        help="Video filters to include in addition to the default video filters. See video_filters for supported values",
    )

    video_parser.add_argument(
        "-vpre",
        "--video-preset",
        dest="video_preset",
        default=VideoWriter.DEFAULT_VIDEO_PRESET,
        help="Tunes the time that FFMPEG will spend optimizing compression while writing the music video to file. See FFMPEG documentation for more info",
    )
    video_parser.add_argument(
        "-vcod",
        "--video-codec",
        dest="video_codec",
        default=VideoWriter.DEFAULT_VIDEO_CODEC,
        help="The video codec for the music video. Supports any codec supported by FFMPEG",
    )
    video_parser.add_argument(
        "-vcrf",
        "--video-crf",
        dest="video_crf",
        type=int,
        default=VideoWriter.DEFAULT_VIDEO_CRF,
        help="The crf quality value for the music video. Takes an integer from 0 (lossless) to 51 (lossy)",
    )
    video_parser.add_argument(
        "-vdim",
        "--video-dimensions",
        dest="video_dimensions",
        type=int,
        nargs=2,
        help="""The pixel dimensions for the music video, width and height.
         All video segments will be resized (cropped and/or scaled) appropriately
         to match these dimensions. Otherwise, the largest dimensions available are used.
         Takes width then height integer values separated by spaces e.g., 1920 1080""",
    )
    video_parser.add_argument(
        "-vasp",
        "--video-aspect-ratio",
        dest="video_aspect_ratio",
        type=Fraction,
        help="The aspect ratio for the music video (overruled by --dimensions). Takes a fraction. i.e.) 16/9",
    )

    video_parser.add_argument(
        "-ss",
        "--save-segments",
        dest="save_segments",
        action="store_true",
        default=False,
        help="Save all the individual segments that compose the music video.",
    )
    video_parser.add_argument(
        "-srs",
        "--save-rejected-segments",
        dest="save_rejected_segments",
        action="store_true",
        default=False,
        help="Save all rejected segments that did not pass filters.",
    )

    return video_parser


def get_event_parser():
    event_parser = argparse.ArgumentParser(add_help=False)

    event_parser.add_argument(
        "-d",
        "--duration",
        dest="duration",
        type=float,
        help="Manually set the duration of the music video",
    )
    event_parser.add_argument(
        "-el",
        "--event-locations",
        dest="event_locations",
        type=float,
        nargs="+",
        help="""Manually enter event locations in seconds for the audio file.
         Usually this corresponds to beats in the music, or any location where one feels
         there should be a cut between clips in the music video.
         If this option is specified alongside --audio-events-mode, both will be combined.
         Takes a list of numerical values separated by spaces""",
    )
    event_parser.add_argument(
        "-eo",
        "--events-offset",
        dest="events_offset",
        type=float,
        help="Global offset for event locations in seconds."
        "If using -es/--events-speed and events are not showing up where desired, try using -eso/--events-speed-offset before this option.",
    )
    event_parser.add_argument(
        "-es",
        "--events-speed",
        dest="events_speed",
        type=Fraction,
        help="Global speed up or slow down for events in the music video. "
        "Should be of the form x or 1/x, where x is a natural number. "
        "(e.g.) 2 for double speed, or 1/2 for half speed. "
        "For slowdown multipliers, events are merged towards the left "
        "(e.g.) Given beat events 1, 2, 3, 4, a slowdown of 1/2 would result in preserving events 1 and 3",
    )
    event_parser.add_argument(
        "-eso",
        "--events-speed-offset",
        dest="events_speed_offset",
        type=int,
        help="Offset for the merging of events on a slowdown speed multiplier. Takes an integer, with a max offset of x - 1 for a slowdown of 1/x",
    )
    event_parser.add_argument(
        "-gebs",
        "--group-events-by-slices",
        dest="group_events_by_slices",
        type=slice,
        nargs="+",
        help="""Group events by one or more slices.
         Must be of the form start,stop or (start,stop).
         Events will be grouped starting at "start", up to but not including "stop".
         Groups explicitly specified by slices will become "selected" groups.
         Any surrounding "unselected" groups will be filled in automatically.
         e.g.) If there are 40 events, a slice of (20,30) results in three groups
         (0,20) (20,30) (30,39), with one selected group (20,30)""",
    )
    event_parser.add_argument(
        "-gebt",
        "--group-events-by-type",
        dest="group_events_by_type",
        nargs="*",
        help="""Group events by type. Useful for modes like the weak_beats beats mode.
         e.g.) If our events are: <10 WeakBeat, 20 Beat, 10 WeakBeat>, passing this option
         with WeakBeat will result in three groups (0,9) (9,29) (29,39),
         with two selected groups (0,9) (29,39)""",
    )
    event_parser.add_argument(
        "-tg",
        "--target-groups",
        dest="target_groups",
        default=TargetGroups.SELECTED,
        help=f"""Which groups --group-by modifiers should apply to.
         Either all groups, only selected groups, or only unselected groups.
         Supported values are {[e.value for e in TargetGroups]}""",
    )
    event_parser.add_argument(
        "-gs",
        "--group-speeds",
        dest="group_speeds",
        type=Fraction,
        nargs="+",
        default=[],
        help=f"""Speed multipliers for event groups created by '--group-by' options.
         e.g.) 1/2 1/4 1/8 will speed multiply all of (0,20) (20,30) (30,39), in order.
         But 1/2 with --target-groups {TargetGroups.SELECTED} will speed multiply only (20,30)""",
    )
    event_parser.add_argument(
        "-gso",
        "--group-speed-offsets",
        dest="group_speed_offsets",
        type=int,
        default=[],
        nargs="+",
        help="Speed multiplier offsets for event group speeds",
    )

    return event_parser
