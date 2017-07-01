import argparse
import logging
import os
import re
import sys
from enum import Enum
from fractions import Fraction

from mugen import constants as c
from mugen import paths
from mugen import utility as util
from mugen import MusicVideoGenerator, Audio, VideoFilter
from mugen.audio.Audio import AudioEventsMode, BeatsMode, OnsetsMode
from mugen.video.events import VideoEventsMode
from mugen.video.MusicVideoGenerator import PreviewMode

import mugen.video.VideoWriter as Vw
import mugen.video.video_filters as vf

import bin.utility as cli_util
import bin.constants as cli_c
from mugen.events import EventList, EventGroupList


class TargetGroups(str, Enum):
    ALL = 'all'
    SELECTED = 'selected'
    UNSELECTED = 'unselected'

debug = False


def create_music_video(args):
    output_directory = args.output_directory
    video_name = args.video_name

    audio_source = args.audio_source
    video_sources = args.video_sources
    video_source_weights = args.video_source_weights

    video_filters = args.video_filters
    exclude_video_filters = args.exclude_video_filters
    include_video_filters = args.include_video_filters

    use_original_audio = args.use_original_audio
    video_dimensions = args.video_dimensions
    video_aspect_ratio = args.video_aspect_ratio
    video_preset = args.video_preset
    video_codec = args.video_codec
    video_crf = args.video_crf
    audio_codec = args.audio_codec
    audio_bitrate = args.audio_bitrate

    save_segments = args.save_segments

    # Prepare Inputs
    audio_file = audio_source if audio_source else cli_util.prompt_file_selection(c.FileType.AUDIO)
    if video_sources:
        video_source_files = cli_util.video_files_from_sources(video_sources)
    else:
        video_source_files = cli_util.prompt_files_selection(c.FileType.VIDEO)

    generator = MusicVideoGenerator(audio_file, video_source_files=video_source_files,
                                    video_source_weights=video_source_weights,
                                    video_filters=video_filters,
                                    exclude_video_filters=exclude_video_filters,
                                    include_video_filters=include_video_filters)

    cli_util.print_weight_stats(generator)

    events = prepare_events(generator.audio, args)

    print("\nGenerating music video from video segments and audio...")

    music_video = generator.generate_from_audio_events(events)

    # Create the directory for the music video
    music_video_name = cli_util.get_music_video_name(output_directory, video_name)
    music_video_directory = os.path.join(output_directory, music_video_name)
    output_path = os.path.join(music_video_directory, music_video_name + Vw.DEFAULT_VIDEO_EXTENSION)
    util.ensure_dir(music_video_directory)

    # Print stats for rejected video segments
    cli_util.print_rejected_segment_stats(generator)

    print(f"\nWriting music video '{output_path}'...")

    # Save the music video
    if video_preset:
        music_video.writer.preset = video_preset
    if video_codec:
        music_video.writer.codec = video_codec
    if video_crf:
        music_video.writer.crf = video_crf
    if audio_codec:
        music_video.writer.audio_codec = audio_codec
    if audio_bitrate:
        music_video.writer.audio_bitrate = audio_bitrate
    music_video.write_to_video_file(output_path, dimensions=video_dimensions, aspect_ratio=video_aspect_ratio,
                                    use_original_audio=use_original_audio)

    # Save the individual segments if asked to do so
    if save_segments:
        print("\nSaving video segments...")
        music_video.write_video_segments(music_video_directory, dimensions=video_dimensions,
                                         aspect_ratio=video_aspect_ratio)


def recreate_music_video(args):
    return


def preview_audio(args):
    output_directory = args.output_directory

    audio_source = args.audio_source
    audio_events_mode = args.audio_events_mode
    preview_mode = args.preview_mode

    # Prepare Inputs
    audio_file = audio_source if audio_source else cli_util.prompt_file_selection(c.FileType.AUDIO)
    filename = paths.filename_from_path(audio_file)
    output_extension = '.wav' if preview_mode == PreviewMode.AUDIO else Vw.DEFAULT_VIDEO_EXTENSION
    output_path = os.path.join(output_directory, filename + "_marked_audio_preview_" + audio_events_mode +
                               output_extension)

    generator = MusicVideoGenerator(audio_file, None)
    events = prepare_events(generator.audio, args)

    print(f"\nCreating audio preview '{paths.filename_from_path(output_path)}'...")

    generator.preview_events(events, output_path, preview_mode)


def prepare_events(audio: Audio, args) -> EventList:
    audio_events_mode = args.audio_events_mode
    beats_mode = args.beats_mode
    onsets_mode = args.onsets_mode
    event_locations = args.event_locations
    events_offset = args.events_offset
    events_speed = args.events_speed
    events_speed_offset = args.events_speed_offset
    group_events_by_slices = args.group_events_by_slices
    group_events_by_type = args.group_events_by_type
    target_groups = args.target_groups
    group_speeds = args.group_speeds
    group_speed_offsets = args.group_speed_offsets

    if event_locations:
        events = EventList(event_locations)
    else:
        print(f"\nAnalyzing audio...")

        if audio_events_mode == AudioEventsMode.BEATS:
            events = audio.beats(beats_mode)
        elif audio_events_mode == AudioEventsMode.ONSETS:
            events = audio.onsets(onsets_mode)
        else:
            print("\nMust provide either events mode or event locations.")
            sys.exit(1)

    if events_speed:
        events.speed_multiply(events_speed, events_speed_offset)

    if group_events_by_type is not None or group_events_by_slices:
        if group_events_by_type is not None:
            event_groups = events.group_by_type(select_types=group_events_by_type)
        else:
            event_groups = events.group_by_slices(slices=group_events_by_slices)

        if target_groups == TargetGroups.ALL:
            event_groups.speed_multiply(group_speeds, group_speed_offsets)
        elif target_groups == TargetGroups.SELECTED:
            event_groups.selected_groups.speed_multiply(group_speeds, group_speed_offsets)
        elif target_groups == TargetGroups.UNSELECTED:
            event_groups.unselected_groups.speed_multiply(group_speeds, group_speed_offsets)

        print(f"\nEvents: \n{event_groups}")

        events = event_groups.flatten()
    else:
        event_groups = EventGroupList([events])
        print(f"\nEvents: {event_groups}")

    if events_offset:
        events.offset(events_offset)

    return events


def getattr_none(*args, **kwargs):
    return getattr(*args, None, **kwargs)


def setup(args):
    # Configuration
    global debug
    debug = args.debug
    if debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    # Make sure output folder is created
    util.ensure_dir(args.output_directory)


def prepare_args(args):
    """
    Formats and validates program inputs
    """
    # sources = [getattrNone(args, 'audio_source'), getattrNone(args, 'video_sources'), getattrNone(args, 'spec_src')]
    # sources = [src for src in sources if src is not None]
    # cli_util.validate_path(*[sources])

    if getattr_none(args, 'video_dimensions') is not None:
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
    except:
        raise argparse.ArgumentTypeError(f"Improper tuple {arg}. Tuple must be of the form x,y or (x,y)")
    else:
        return x, y


class HelpParser(argparse.ArgumentParser):
    """
    Custom Parser which prints help on error
    """
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def parse_args(args):
    parser = HelpParser()
    event_parser = argparse.ArgumentParser(add_help=False)
    video_parser = argparse.ArgumentParser(add_help=False) 
    audio_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    """ PARSERS """

    parser.add_argument('-db', '--debug', dest='debug', action='store_true', default=False,
                        help='Pass in this argument to print useful debug info.')
    parser.add_argument('-od', '--output-directory', dest='output_directory', default=cli_c.OUTPUT_PATH_BASE,
                        help='The directory in which to store any output from this program. '
                             'Will create the directory if non-existent. Default is ' + cli_c.OUTPUT_PATH_BASE)

    # Event Common Parameters
    event_parser.add_argument('-el', '--event-locations', dest='event_locations', type=float, nargs='+',
                              help='Event locations for the audio file. '
                                   'Usually this corresponds to beats in the music, or any location where one feels '
                                   'there should be a cut between clips in the music video. Takes a list of numerical '
                                   'values separated by spaces.')
    event_parser.add_argument('-eo', '--events-offset', dest='events_offset', type=float,
                              help='Global offset for event locations.')
    event_parser.add_argument('-es', '--events-speed', dest='events_speed', type=Fraction,
                              help='Global speed up or slow down for events in the music video. '
                                   'Should be of the form x or 1/x, where x is a natural number. '
                                   '(e.g.) 2 for double speed, or 1/2 for half speed.')
    event_parser.add_argument('-eso', '--events-speed-offset', dest='events_speed_offset', type=int,
                              help='Offset for the merging of events on a slowdown speed multiplier. '
                                   'Takes an integer, with a max offset of x - 1 for a slowdown of 1/x.')
    event_parser.add_argument('-gebs', '--group-events-by-slices', dest='group_events_by_slices', type=slice, nargs='+',
                              help='Group events by one or more slices. '
                                   'Must be of the form start,stop or (start,stop). '
                                   'Events will be grouped starting at "start", up to but not including "stop". '
                                   'Groups explicitly specified by slices will become "selected" groups. '
                                   'Any surrounding "unselected" groups will be filled in automatically. '
                                   'e.g.) If there are 40 events, a slice of (20,30) results in three groups '
                                   '(0,20) (20,30) (30,39), with one selected group (20,30)')
    event_parser.add_argument('-gebt', '--group-events-by-type', dest='group_events_by_type', nargs='*',
                              help='Group events by type. Useful for modes like the "weak_beats" beats mode. '
                                   'e.g.) If our events are: <10 weak_beat, 20 beat, 10 weak_beat>, '
                                   'passing this option with "weak_beat" will result in three groups '
                                   '(0,9) (9,29) (29,39), with two selected groups (0,9) (29,39)')
    event_parser.add_argument('-tg', '--target-groups', dest='target_groups', default=TargetGroups.SELECTED,
                              help='Which groups "--group-by" modifiers should apply to. '
                                   'Either all groups, only selected groups, or only unselected groups. '
                                   f'Default is {TargetGroups.SELECTED}. '
                                   f'Supported values are {[e.value for e in TargetGroups]}.')
    event_parser.add_argument('-gs', '--group-speeds', dest='group_speeds', type=Fraction, nargs='+',
                              default=[],
                              help='Speed multipliers for event groups created by "--group-by" options. '
                                   f'e.g.) 1/2 1/4 1/8 will speed multiply all of (0,20) (20,30) (30,39), in order. '
                                   f'But 1/2 with --target-groups {TargetGroups.SELECTED} will speed multiply only '
                                   f'(20,30).')
    event_parser.add_argument('-gso', '--group-speed-offsets', dest='group_speed_offsets', type=int,
                              default=[], nargs='+',
                              help='Speed multiplier offsets for event group speeds.')

    # Video Common Parameters
    video_parser.add_argument('-vn', '--video-name', dest='video_name', default=cli_c.DEFAULT_MUSIC_VIDEO_NAME,
                              help=f'The name for the music video. '
                                   f'Otherwise will output {cli_c.DEFAULT_MUSIC_VIDEO_NAME}_0, '
                                   f'{cli_c.DEFAULT_MUSIC_VIDEO_NAME}_1, etc...')

    video_parser.add_argument('-vem', '--video-events-mode', dest='video_events_mode',
                              help=f'Method of generating video events for the music video. '
                                   f'Supported values are {[e.value for e in VideoEventsMode]}')
    video_parser.add_argument('-vf', '--video-filters', dest='video_filters', nargs='+',
                              help=f'Video filters that each segment in the music video must pass. '
                                   f'Defaults are {[filter for filter in vf.VIDEO_FILTERS_DEFAULT]}'
                                   f'Supported values are {[filter.name for filter in VideoFilter]}. ')
    video_parser.add_argument('-evf', '--exclude-video-filters', dest='exclude_video_filters', nargs='+',
                              help=f'Video filters to exclude from the default video filters. '
                                   f'See video_filters for supported values')
    video_parser.add_argument('-ivf', '--include-video-filters', dest='include_video_filters', nargs='+',
                              help=f'Video filters to include in addition to the default video filters. '
                                   f'See video_filters for supported values')

    video_parser.add_argument('-vpre', '--video-preset', dest='video_preset',
                              help=f'Tunes the time that FFMPEG will spend optimizing compression while writing '
                                   f'the music video to file. Default is {Vw.DEFAULT_VIDEO_PRESET}')
    video_parser.add_argument('-vcod', '--video-codec', dest='video_codec',
                              help=f'The video codec for the music video. Default is {Vw.DEFAULT_VIDEO_CODEC}')
    video_parser.add_argument('-vcrf', '--video-crf', dest='video_crf', type=int,
                              help=f'The crf quality value for the music video. '
                                   f'Takes an integer from 0 (lossless) to 51 (lossy). '
                                   f'Default is {Vw.DEFAULT_VIDEO_CRF}')
    video_parser.add_argument('-vdim', '--video-dimensions', dest='video_dimensions', type=int, nargs=2,
                              help='The pixel dimensions for the music video, width and height. '
                                   'All video segments will be resized (cropped and/or scaled) appropriately '
                                   'to match these dimensions. Otherwise, the largest dimensions available are used. '
                                   'Takes width then height integer values separated by spaces e.g., 1920 1080')
    video_parser.add_argument('-vasp', '--video-aspect-ratio', dest='video_aspect_ratio', type=Fraction,
                              help='The aspect ratio for the music video (overruled by --dimensions).'
                                   'Takes a fraction. i.e.) 16/9')

    video_parser.add_argument('-ss', '--save-segments', dest='save_segments', action='store_true', default=False,
                              help='Save all the individual segments that compose the music video.')

    # Audio Common Parameters
    audio_parser.add_argument('-a', '--audio-source', dest='audio_source',
                              help='The audio file for the music video. '
                                   'Supports any audio format supported by ffmpeg, '
                                   'such as wav, aiff, flac, ogg, mp3, etc...')
    audio_parser.add_argument('-uoa', '--use-original-audio', dest='use_original_audio', action='store_true',
                              default=False,
                              help=f"Whether or not to use the original audio from video segments for the music video. "
                                   f"Defaults to False.")

    audio_parser.add_argument('-aem', '--audio-events-mode', dest='audio_events_mode', default=AudioEventsMode.BEATS,
                              help=f'Method of generating events from the audio file. '
                                   f'Default is {AudioEventsMode.BEATS}. '
                                   f'Supported values are {[e.value for e in AudioEventsMode]}.')

    audio_parser.add_argument('-bm', '--beats-mode', dest='beats_mode', default=BeatsMode.BEATS,
                              help=f'Method of generating beat events from the audio file. '
                                   f'Default is {BeatsMode.BEATS}. '
                                   f'Supported values are {[e.value for e in BeatsMode]}.')
    audio_parser.add_argument('-om', '--onsets-mode', dest='onsets_mode', default=OnsetsMode.ONSETS,
                              help=f'Method of generating onset events from the audio file. '
                                   f'Supported values are {[e.value for e in OnsetsMode]}.')

    audio_parser.add_argument('-ac', '--audio-codec', dest='audio_codec',
                              help=f'The audio codec for the music video if the original audio is used. '
                                   f'Default is {Vw.DEFAULT_AUDIO_CODEC}')
    audio_parser.add_argument('-ab', '--audio-bitrate', dest='audio_bitrate', type=int,
                              help='The audio bitrate for the music video if no audio_file is given. '
                                   f'Default is {Vw.DEFAULT_AUDIO_BITRATE} (kbps)')

    """ COMMANDS """

    # Create Command Parameters
    create_parser = subparsers.add_parser('create', parents=[audio_parser, video_parser, event_parser],
                                          help='Create a new music video.')
    create_parser.set_defaults(func=create_music_video)
    create_parser.add_argument('-v', '--video-sources', dest='video_sources', nargs='+',
                               help='The video sources for the music video. '
                                    'Takes a list of files and folders separated by spaces. '
                                    'Supports any video format supported by ffmpeg, '
                                    'such as .ogv, .mp4, .mpeg, .avi, .mov, etc...')
    create_parser.add_argument('-vw', '--video-source-weights', dest='video_source_weights', type=float, nargs='+',
                               default=[],
                               help='Weights for controlling how often each video source should be used '
                                    'in the music video. Takes a list of numbers separated by spaces. '
                                    '(i.e.) Pass --weights .6 .4 or --weights 6 4 to use the first video source '
                                    '(a series of 26 episodes) 60%% of the time, and the second video source '
                                    '(a movie) 40%% of the time.')

    # Recreate Command Parameters
    recreate_parser = subparsers.add_parser('recreate', parents=[video_parser],
                                            help="Recreate a music video from a spec file.")
    recreate_parser.set_defaults(func=recreate_music_video)
    recreate_parser.add_argument('-s', '--spec-source', dest='spec_src',
                                 help='The spec file from which to recreate the music video. '
                                      'Spec files are generated alongside music videos created by this program.')
    recreate_parser.add_argument('-rs', '--replace-segments', dest='replace_segments', type=int, nargs='+',
                                 help='Pass in this argument to provide a list of segment numbers in the music video '
                                      'to replace with new random segments. '
                                      'Takes values separated by spaces (e.g.) 98 171 200 305.')

    # Preview Command Parameters
    preview_parser = subparsers.add_parser('preview', parents=[audio_parser, event_parser],
                                           help="Create an audio preview of events for a music video by marking "
                                                "the audio with bleeps.")
    preview_parser.add_argument('-pm', '--preview-mode', dest='preview_mode', default=PreviewMode.VISUAL,
                                help=f'The method of previewing events. Default is {PreviewMode.VISUAL}. '
                                     f'Supported values are {[e.value for e in PreviewMode]}')
    preview_parser.set_defaults(func=preview_audio)

    # Exit if no args passed in
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    args = prepare_args(args)
    setup(args)
    args.func(args)

    print("\nAll Done!")


