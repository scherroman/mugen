import argparse
import logging
import os
import sys
from fractions import Fraction

from mugen import constants as c
from mugen import paths
from mugen import utility as util
from mugen.events import EventsModifier
from mugen import preview, MusicVideoGenerator, AudioEventsMode, VideoEventsMode, VideoFilter

import mugen.video.VideoWriter as vw
import mugen.video.video_filters as vf

import bin.utility as cli_util
import bin.constants as cli_c

HELP = "Please review supported inputs on the help menu via --help"

debug = False


def create_music_video(args):
    output_directory = args.output_directory
    video_name = args.video_name
    video_extension = args.video_extension

    audio_source = args.audio_source
    video_sources = args.video_sources
    video_source_weights = args.video_source_weights
    audio_events_mode = args.audio_events_mode
    video_events_mode = args.video_events_mode
    event_locations = args.event_locations

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
    events_offset = args.events_offset
    events_speed_multiplier = args.events_speed_multiplier
    events_speed_multiplier_offset = args.events_speed_multiplier_offset

    save_segments = args.save_segments
    save_rejected_segments = args.save_rejected_segments

    # Prepare Inputs
    audio_file = audio_source if audio_source else cli_util.prompt_file_selection(c.FileType.AUDIO)
    if video_sources:
        video_source_files = cli_util.video_files_from_sources(video_sources)
    else:
        video_source_files = cli_util.prompt_files_selection(c.FileType.VIDEO)

    event_modifiers = {EventsModifier.SPEED_MULTIPLIER: events_speed_multiplier,
                       EventsModifier.SPEED_MULTIPLIER_OFFSET: events_speed_multiplier_offset,
                       EventsModifier.OFFSET: events_offset}
    music_video_generator = MusicVideoGenerator(audio_file, video_source_files=video_source_files,
                                                video_source_weights=video_source_weights,
                                                video_filters=video_filters,
                                                exclude_video_filters=exclude_video_filters,
                                                include_video_filters=include_video_filters)

    cli_util.print_weight_stats(music_video_generator)
    print("\nGenerating music video from video segments and audio...")

    if event_locations:
        music_video = music_video_generator.generate_from_event_locations(event_locations, video_events_mode,
                                                                          event_modifiers=event_modifiers)
    else:
        music_video = music_video_generator.generate_from_audio_events(audio_events_mode, video_events_mode,
                                                                       event_modifiers=event_modifiers)

    # Create the directory for the music video
    music_video_name = video_name if video_name else cli_util.get_music_video_name(output_directory, video_name)
    music_video_directory = os.path.join(output_directory, music_video_name)
    output_path = os.path.join(music_video_directory, music_video_name + video_extension)
    util.ensure_dir(music_video_directory)

    print(f"\n\nWriting video {output_path}")

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

    # print("Saving music video spec...")
    #
    # # Save reusable spec for the music video
    # spec = v_io.save_music_video_spec(audio_file, source_videos, events_speed_multiplier,
    #                                   events_speed_multiplier_offset, beat_stats, beat_interval_groups,
    #                                   video_segments)

    # v_io.add_auxiliary_tracks(music_video, temp_output_path, output_path)

    # Print stats for rejected video segments
    cli_util.print_rejected_segment_stats(music_video)

    # Save the individual segments if asked to do so
    if save_segments:
        print("\nSaving video segments...")
        music_video.save_video_segments(music_video_directory)

    # Save the video segments that were rejected
    if save_rejected_segments:
        print("\nSaving rejected segments...")
        music_video.save_video_segments(music_video_directory, rejected=True)


def recreate_music_video(args):
    return
    # video_name = args.video_name
    # c.music_video_crf = args.crf
    # audio_codec = args.audio_codec
    # audio_bitrate = args.audio_bitrate
    # video_dimensions = args.video_dimensions
    # preserve_video_dimensions = args.preserve_video_dimensions
    # c.allow_repeats = args.allow_repeats
    # save_segments = args.save_segments
    # spec_src = args.spec_src
    # replace_segments = args.replace_segments
    #
    # # Prepare Inputs
    # music_video_name = video_name if video_name else bin.get_music_video_name("regenerated_")
    # spec_file = spec_src if spec_src else bin.prompt_file_selection(c.FileType.SPEC)
    # spec = util.parse_spec_file(spec_file)
    # if replace_segments:
    #     bin.validate_replace_segments(replace_segments, spec['video_segments'])
    # video_files = [video_file['file_path'] for video_file in spec['video_files']]
    # audio_source = spec['audio_file']['file_path']
    # audio_offset = spec['audio_file']['offset']
    # audio_file = audio_source if audio_source else bin.prompt_file_selection(c.FileType.AUDIO)
    #
    # # Reserve file for music video
    # v_util.reserve_music_video_file(music_video_name)
    #
    # # Set dimensions for music video
    # if not preserve_video_dimensions:
    #     c.music_video_dimensions = (video_dimensions if video_dimensions
    #                                 else v_sizing.largest_dimensions_with_aspect_ratio(video_files))
    #
    # # Offset the audio if specified in spec
    # if audio_offset and audio_offset > 0:
    #     print("Creating temporary audio file with specified offset {}...".format(audio_offset))
    #     audio_file = audio.create_temp_offset_audio_file(audio_file, audio_offset)
    #
    # # Regenerate the video segments from the spec file
    # regen_video_segments = video.regenerate_video_segments(spec, replace_segments)
    #
    # # Save regenerated spec for the music video
    # regenerated_spec = v_io.save_regenerated_music_video_spec(spec, regen_video_segments)
    #
    # # Compile music video from video segments and audio
    # print("Generating music video from video segments and audio...")
    # video.create_music_video(regen_video_segments, audio_file, regenerated_spec)
    #
    # v_io.add_auxiliary_tracks(music_video, temp_output_path, output_path)
    #
    # # Save the individual segments if asked to do so
    # if save_segments:
    #     print("Saving video segments...")
    #     v_io.save_video_segments(regen_video_segments)


def preview_audio(args):
    output_directory = args.output_directory

    audio_source = args.audio_source
    audio_events_mode = args.audio_events_mode
    event_locations = args.event_locations
    events_offset = args.events_offset
    events_speed_multiplier = args.events_speed_multiplier
    events_speed_multiplier_offset = args.events_speed_multiplier_offset

    # Prepare Inputs
    audio_file = audio_source if audio_source else cli_util.prompt_file_selection(c.FileType.AUDIO)
    filename = paths.filename_from_path(audio_file)
    output_path = os.path.join(output_directory, filename + "_marked_audio_preview_" + audio_events_mode + '.wav')

    print(f"Creating audio preview {paths.filename_from_path(output_path)}...")

    event_modifiers = {EventsModifier.SPEED_MULTIPLIER: events_speed_multiplier,
                       EventsModifier.SPEED_MULTIPLIER_OFFSET: events_speed_multiplier_offset,
                       EventsModifier.OFFSET: events_offset}

    if event_locations:
        preview.preview_event_locations(audio_file, event_locations, output_path, event_modifiers=event_modifiers)
    elif audio_events_mode:
        preview.preview_audio_events(audio_file, audio_events_mode, output_path, event_modifiers=event_modifiers)
    else:
        print("Must provide either event locations or method for generating events.")
        sys.exit(1)


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
    if getattr_none(args, 'video_aspect_ratio') is not None:
        args.video_dimensions = tuple(args.video_aspect_ratio)

    return args


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
    video_parser = argparse.ArgumentParser(add_help=False) 
    audio_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    """ SHARED PARAMETERS """

    parser.add_argument('-db', '--debug', dest='debug', action='store_true', default=False,
                        help='Pass in this argument to print useful debug info.')
    parser.add_argument('-od', '--output-directory', dest='output_directory', default=cli_c.OUTPUT_PATH_BASE,
                        help='The directory in which to store any output from this program. Will create the directory if nonexistant. Default is ' + cli_c.OUTPUT_PATH_BASE)
    parser.add_argument('-el', '--event-locations', dest='event_locations', type=float, nargs='+',
                        help='Event locations for the audio file. Usually this corresponds to beats in the music, or any location where one feels there should be a visual effect or cut between clips in the music video. Takes a list of numerical values separated by spaces.')
    parser.add_argument('-eo', '--events-offset', dest='events_offset', type=float,
                        help='Global offset for event locations.')
    parser.add_argument('-esm', '--events-speed-multiplier', dest='events_speed_multiplier', type=Fraction, default=1,
                        help='Speed up or slow down the occurence of event in the music video. Should be of the form x or 1/x, where x is a natural number. (e.g.) 2 for double speed, or 1/2 for half speed.')
    parser.add_argument('-esmo', '--events-speed-multiplier-offset', dest='events_speed_multiplier_offset', type=int,
                        help='Used alongside a slowdown speed multiplier to offset the merging of events. Takes an integer, with a max offset of x - 1 for a slowdown of 1/x.')

    # Video Common Parameters
    video_parser.add_argument('-vn', '--video-name', dest='video_name',
                              help=f'The name for the music video. Otherwise will output {cli_c.DEFAULT_MUSIC_VIDEO_NAME}_0, {cli_c.DEFAULT_MUSIC_VIDEO_NAME}_1, etc...')
    video_parser.add_argument('-ve', '--video-extension', dest='video_extension', default=vw.DEFAULT_VIDEO_EXTENSION,
                              help=f'The file extension for the music video. Default is {vw.DEFAULT_VIDEO_EXTENSION}')
    video_parser.add_argument('-vem', '--video-events-mode', dest='video_events_mode',
                              help=f"Method of generating video events for the music video. Supported values are {[e.value for e in VideoEventsMode]}")
    video_parser.add_argument('-vf', '--video-filters', dest='video_filters', nargs='+',
                              help=f"Video filters that each segment in the music video must pass. Supported values are {[filter.name for filter in VideoFilter]}. Defaults are {[filter for filter in vf.VIDEO_FILTERS_DEFAULT]}")
    video_parser.add_argument('-evf', '--exclude-video-filters', dest='exclude_video_filters', nargs='+',
                              help=f"Video filters to exclude from the default video filters. See video_filters for supported values")
    video_parser.add_argument('-ivf', '--include-video-filters', dest='include_video_filters', nargs='+',
                              help=f"Video filters to include in addition to the default video filters. See video_filters for supported values")
    video_parser.add_argument('-vpre', '--video-preset', dest='video_preset',
                              help=f'Tunes the time that FFMPEG will spend optimizing compression while writing the music video to file. Default is {vw.DEFAULT_VIDEO_PRESET}')
    video_parser.add_argument('-vcod', '--video-codec', dest='video_codec',
                              help=f'The video codec for the music video. Default is {vw.DEFAULT_VIDEO_CODEC}')
    video_parser.add_argument('-vcrf', '--video-crf', dest='video_crf', type=int,
                              help=f'The crf quality value for the music video. Takes an integer from 0 (lossless) to 51 (lossy). Default is {vw.DEFAULT_VIDEO_CRF}')
    video_parser.add_argument('-vdim', '--video-dimensions', dest='video_dimensions', type=int, nargs=2,
                              help='The pixel dimensions for the music video, width and height. All video segments will be resized (cropped and/or scaled) appropriately to match these dimensions. Otherwise, the best dimensions for the music video are calculated automatically. Takes width then height integer values separated by spaces e.g., 1920 1080')
    video_parser.add_argument('-vasp', '--video-aspect-ratio', dest='video_aspect_ratio', type=float, nargs=2,
                              help='The aspect ratio for the music video (overruled by --dimensions).')
    video_parser.add_argument('-ss', '--save-segments', dest='save_segments', action='store_true', default=False,
                              help='Save all the individual segments that compose the music video.')

    # Audio Common Parameters
    audio_parser.add_argument('-a', '--audio-source', dest='audio_source',
                              help='The audio file for the music video. Supports any audio format supported by ffmpeg, such as wav, aiff, flac, ogg, mp3, etc...')
    audio_parser.add_argument('-aem', '--audio-events-mode', dest='audio_events_mode',
                              help=f"Method of generating events from the audio file. Supported values are {[e.value for e in AudioEventsMode]}.")
    audio_parser.add_argument('-uoa', '--use-original-audio', dest='use_original_audio', action='store_true', default=False,
                              help=f"Whether or not to use the original audio from video segments for the music video. Defaults to False.")
    audio_parser.add_argument('-ac', '--audio-codec', dest='audio_codec',
                              help='The audio codec for the music video if the original audio is used. Default is mp3')
    audio_parser.add_argument('-ab', '--audio-bitrate', dest='audio_bitrate', type=int,
                              help='The audio bitrate for the music video if no audio_file is given. Default is 320 (kbps)')

    """ COMMANDS """
 
    # Create Command Parameters
    create_parser = subparsers.add_parser('create', parents=[audio_parser, video_parser],
                                          help="Create a new music video.")
    create_parser.set_defaults(func=create_music_video)
    create_parser.add_argument('-v', '--video-sources', dest='video_sources', nargs='+',
                               help='The video sources for the music video. Takes a list of files and folders separated by spaces. Supports any video format supported by ffmpeg, such as .ogv, .mp4, .mpeg, .avi, .mov, etc...')
    create_parser.add_argument('-vw', '--video-source-weights', dest='video_source_weights', type=float, nargs='+', default=[],
                               help='Weights for controlling how often each video source should be used in the music video. Takes a list of numbers separated by spaces. (i.e.) Pass --weights .6 .4 or --weights 6 4 to use the first video source (a series of 26 episodes) 60% of the time, and the second video source (a movie) 40% of the time.')
    create_parser.add_argument('-sx', '--save-rejected-segments', dest='save_rejected_segments', action='store_true', default=False,
                               help='Pass in this argument to save all segments that were rejected from the music video.')

    # Recreate Command Parameters
    recreate_parser = subparsers.add_parser('recreate', parents=[video_parser],
                                            help="Recreate a music video from a spec file.")
    recreate_parser.set_defaults(func=recreate_music_video)
    recreate_parser.add_argument('-s', '--spec-source', dest='spec_src',
                                 help='The spec file from which to recreate the music video. Spec files are generated alongside music videos created by this program.')
    recreate_parser.add_argument('-rs', '--replace-segments', dest='replace_segments', type=int, nargs='+',
                                 help='Pass in this argument to provide a list of segment numbers in the music video to replace with new random segments. Takes values separated by spaces (e.g.) 98 171 200 305.')

    # Preview Command Parameters
    preview_parser = subparsers.add_parser('preview', parents=[audio_parser],
                                           help="Create an audio preview of event locations for a music video by marking the audio with bleeps.")
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


