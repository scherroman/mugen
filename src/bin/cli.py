import argparse
import atexit
import logging
import os
import sys
from fractions import Fraction

from mugen import constants as c
from mugen import paths
from mugen import utility as util
from mugen.exceptions import ParameterError
from mugen.video import constants as vc
from mugen.audio import constants as ac
from mugen.audio import preview
from mugen.audio.preview import AudioEvents
from mugen.video import sizing as v_sizing, io as v_io, utility as v_util
from mugen.video.MusicVideoGenerator import MusicVideoGenerator

import bin.utility as clu

HELP = " Please review supported inputs and values on the help menu via --help"

debug = False


def create_music_video(args):
    return
#     output_directory = args.output_directory
#     output_name = args.output_name
#
#     audio_src = args.audio_src
#     video_src = args.video_src
#     cut_locations = args.cut_intervals
#     cut_intervals = args.cut_intervals
#     video_filters = args.video_filters
#     exclude_video_filters = args.exclude_video_filters
#     include_video_filters = args.include_video_filters
#
#     dimensions = args.dimensions
#     aspect_ratio = args.video_aspect_ratio
#     video_crf = args.crf
#     audio_codec = args.audio_codec
#     audio_bitrate = args.audio_bitrate
#     speed_multiplier = args.speed_multiplier
#     speed_multiplier_offset = args.speed_multiplier_offset
#
#     save_segments = args.save_segments
#     save_rejected_segments = args.save_rejected_segments
#

    # # Prepare Inputs
    # music_video_name = output_name if output_name else bin.get_music_video_name()
    # audio_file = audio_src if audio_src else bin.prompt_file_selection(c.FileType.AUDIO)
    # video_files = util.get_files(video_src) if video_src else bin.prompt_files_selection(c.FileType.VIDEO)
    #
    # print("Preparing {}...".format(music_video_name))
    # logging.debug("Audio File {}".format(audio_file))
    # logging.debug("Video Files {}".format(video_files))
    #
    # # Reserve directory for music video
    # util.ensure_dir(music_video_directory)
    #
    # # Set dimensions for music video
    # if not preserve_video_dimensions:
    #     c.music_video_dimensions = (video_dimensions if video_dimensions
    #                                 else v_sizing.largest_dimensions_with_aspect_ratio(video_files))
    #
    # # Get beat intervals & other stats from audio file
    # print("Finding beat locations from audio...")
    # beat_stats = audio.get_beat_stats(audio_file)
    #
    # # Assign beat intervals to groups based on speed_multiplier
    # beat_interval_groups = audio.get_beat_interval_groups(beat_stats['beat_intervals'], speed_multiplier,
    #                                                       speed_multiplier_offset)
    #
    # # Generate random video segments according to beat intervals
    # print("Sampling video segments from {} videos according to beat patterns...".format(len(video_files)))
    # video_segments, rejected_segments = video.generate_video_segments(video_files, beat_interval_groups)
    #
    # print("Saving music video spec...")
    #
    # # Save reusable spec for the music video
    # spec = v_io.save_music_video_spec(audio_file, video_files, speed_multiplier,
    #                                   speed_multiplier_offset, beat_stats, beat_interval_groups,
    #                                   video_segments)
    #
    # # Compile music video from video segments and audio
    # print("Generating music video from video segments and audio...")
    # video.create_music_video(video_segments, audio_file, spec)
    #
    # v_io.add_auxiliary_tracks(music_video, temp_output_path, output_path)
    #
    # # Print stats for rejected video segments
    # v_util.print_rejected_segment_stats(rejected_segments)
    #
    # # Save the individual segments if asked to do so
    # if save_segments:
    #     print("Saving video segments...")
    #     v_io.save_video_segments(video_segments)
    #
    # # Save the video segments that were rejected
    # if save_rejected_segments:
    #     print("Saving rejected segments...")
    #     v_io.save_rejected_segments(rejected_segments)


def recreate_music_video(args):
    return
    # output_name = args.output_name
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
    # music_video_name = output_name if output_name else bin.get_music_video_name("regenerated_")
    # spec_file = spec_src if spec_src else bin.prompt_file_selection(c.FileType.SPEC)
    # spec = util.parse_spec_file(spec_file)
    # if replace_segments:
    #     bin.validate_replace_segments(replace_segments, spec['video_segments'])
    # video_files = [video_file['file_path'] for video_file in spec['video_files']]
    # audio_src = spec['audio_file']['file_path']
    # audio_offset = spec['audio_file']['offset']
    # audio_file = audio_src if audio_src else bin.prompt_file_selection(c.FileType.AUDIO)
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

    audio_src = args.audio_src
    method = args.method
    event_locations = args.event_locations
    event_locations_offset = args.event_locations_offset
    speed_multiplier = args.speed_multiplier
    speed_multiplier_offset = args.speed_multiplier_offset

    # Prepare Inputs
    audio_file = audio_src if audio_src else clu.prompt_file_selection(c.FileType.AUDIO)
    filename = paths.filename_from_path(audio_file)
    output_path = clu.audio_preview_path(output_directory, filename)

    print(f"Creating audio preview {output_path}...")

    if event_locations:
        preview.preview_event_locations(audio_file, event_locations, output_path,
                                        event_locations_offset=event_locations_offset,
                                        speed_multiplier=speed_multiplier,
                                        speed_multiplier_offset=speed_multiplier_offset)
    elif method:
        preview.preview_audio_event_locations(audio_file, output_path, method,
                                              event_locations_offset=event_locations_offset,
                                              speed_multiplier=speed_multiplier,
                                              speed_multiplier_offset=speed_multiplier_offset)
    else:
        print("Must provide either event locations or method for generating event locations.")
        sys.exit(1)


# def exit_handler():
#     # Cleanup reserved music video folder if empty
#     if c.music_video_name:
#         reserved_music_video_file = paths.music_video_output_path(c.music_video_name)
#         if os.path.exists(reserved_music_video_file) and os.stat(reserved_music_video_file).st_size == 0:
#             os.remove(reserved_music_video_file)


def getattrNone(*args, **kwargs):
    return getattr(*args, None, **kwargs)


def setup(args):
    # Configuration
    global debug
    debug = args.debug
    if debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    # atexit.register(exit_handler)

    # Make sure output folder is created
    util.ensure_dir(clu.OUTPUT_PATH_BASE)


def prepare_args(args):
    """
    Formats and validates program inputs
    """
    # sources = [getattrNone(args, 'audio_src'), getattrNone(args, 'video_src'), getattrNone(args, 'spec_src')]
    # sources = [src for src in sources if src is not None]
    # clu.validate_path(*[sources])

    if getattrNone(args, 'video_dimensions') is not None:
        args.video_dimensions = tuple(args.video_dimensions)

    return args


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def parse_args(args):
    parser = MyParser()
    video_parser = argparse.ArgumentParser(add_help=False) 
    audio_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    """ SHARED PARAMETERS """

    parser.add_argument('-db', '--debug', dest='debug', action='store_true', default=False,
                        help='Pass in this argument to print useful debug info.')
    parser.add_argument('-od', '--output-directory', dest='output_directory', default = clu.OUTPUT_PATH_BASE,
                        help='The directory in which to store any output from this program. Default is ' + clu.OUTPUT_PATH_BASE)

    # Video Common Parameters
    video_parser.add_argument('-o', '--output-name', dest='output_name',
                              help='The name for the music video. Otherwise will output ' + clu.DEFAULT_MUSIC_VIDEO_NAME + '_0, ' + clu.DEFAULT_MUSIC_VIDEO_NAME + '_1, etc...')
    video_parser.add_argument('-crf', '--crf', dest='crf', type=int, default=vc.DEFAULT_VIDEO_CRF,
                              help='The crf quality value for the music video. Takes an integer from 0 (lossless) to 51 (lossy). Defaults to 18.')
    video_parser.add_argument('-d', '--dimensions', dest='dimensions', type=int, nargs=2,
                              help='Set the pixel dimensions for the music video, width and height. All video segments will be resized (cropped and/or scaled) appropriately to match these dimensions. Otherwise, the best dimensions for the music video are calculated automatically. Takes width then height integer values separated by spaces e.g., 1920 1080')
    video_parser.add_argument('-ar', '--aspect-ratio', dest='aspect-ratio', type=float,
                              help='Set the aspect ratio for the music video (overruled by --dimensions).')
    video_parser.add_argument('-ss', '--save-segments', dest='save_segments', action='store_true', default=False,
                              help='Save all the individual segments that compose the music video.')

    # Audio Common Parameters
    audio_parser.add_argument('-a', '--audio-source', dest='audio_src',
                              help='The audio file for the music video. Supports any audio format supported by ffmpeg, such as wav, aiff, flac, ogg, mp3, etc...')
    audio_parser.add_argument('-el', '--event-locations', dest='event_locations', type=float, nargs='+',
                              help='Event locations for the audio file. Usually this corresponds to beats in the music, or any location where one feels there should be a visual effect or cut between clips in the music video. Takes a list of numerical values separated by spaces.')
    audio_parser.add_argument('-elo', '--event-locations-offset', dest='event_locations_offset', type=float,
                              help='Global offset for event locations.')
    audio_parser.add_argument('-sm', '--speed-multiplier', dest='speed_multiplier', type=Fraction, default=1,
                              help='Speed up or slow down the occurence of event locations in the music video. Should be of the form x or 1/x, where x is a natural number. (e.g.) 2 for double speed, or 1/2 for half speed.')
    audio_parser.add_argument('-smo', '--speed-multiplier-offset', dest='speed_multiplier_offset', type=int,
                              help='Used alongside a slowdown speed multiplier to offset the merging of event locations. Takes an integer, with a max offset of x - 1 for a slowdown of 1/x.')
    audio_parser.add_argument('-ac', '--audio-codec', dest='audio_codec', default=ac.DEFAULT_AUDIO_CODEC,
                              help='The audio codec for the music video if no audio_file is given.')
    audio_parser.add_argument('-ab', '--audio-bitrate', dest='audio_bitrate', type=int, default=ac.DEFAULT_AUDIO_BITRATE,
                              help='The audio bitrate for the music video if no audio_file is given.')

    """ COMMANDS """
 
    # Create Command Parameters
    create_parser = subparsers.add_parser('create', parents=[audio_parser, video_parser],
                                          help="Create a new music video.")
    create_parser.set_defaults(func=create_music_video)
    create_parser.add_argument('-v', '--video-source', dest='video_src', nargs='+',
                               help='The video(s) for the music video. Takes a list of files and folders separated by spaces. Supports any video format supported by ffmpeg, such as .ogv, .mp4, .mpeg, .avi, .mov, etc...')
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
    preview_parser.add_argument('-m', '--method', dest='method', default=AudioEvents.BEATS,
                                help="Method of generating events from the audio file. Supported values are " + str([e.value.lower() for e in AudioEvents]))

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

    print("All Done!")


