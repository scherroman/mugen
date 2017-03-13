import os
import sys
import atexit
import logging
import argparse
from fractions import Fraction

# Add base project module to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Project modules
import mugen.constants as c
import mugen.paths as paths
import mugen.clu as clu
import mugen.utility as util
import mugen.audio.audio as audio
from mugen.video import video, sizing as v_sizing, io as v_io, utility as v_util

def create_music_video(output_name, crf, video_dimensions, preserve_video_dimensions):
    output_name = args.output_name
    c.music_video_crf = args.crf
    video_dimensions = args.video_dimensions
    preserve_video_dimensions = args.preserve_video_dimensions
    c.allow_repeats = args.allow_repeats
    save_segments = args.save_segments
    save_rejected_segments = args.save_rejected_segments
    audio_src = args.audio_src
    video_src = args.video_src
    speed_multiplier = args.speed_multiplier
    speed_multiplier_offset = args.speed_multiplier_offset

    # Prepare Inputs
    music_video_name = output_name if output_name else clu.get_music_video_name()
    audio_file = audio_src if audio_src else clu.prompt_file_selection(c.FileType.AUDIO)
    video_files = util.get_files(video_src) if video_src else clu.prompt_files_selection(c.FileType.VIDEO)

    print("Preparing {}...".format(music_video_name))
    logging.debug("Audio File {}".format(audio_file))
    logging.debug("Video Files {}".format(video_files))

    # Reserve file for music video
    v_util.reserve_music_video_file(music_video_name)

    # Set dimensions for music video
    if not preserve_video_dimensions:
        c.music_video_dimensions = video_dimensions if video_dimensions \
                                   else v_sizing.largest_dimensions_with_aspect_ratio(video_files)

    # Get beat intervals & other stats from audio file
    beat_stats = audio.get_beat_stats(audio_file)

    # Assign beat intervals to groups based on speed_multiplier
    beat_interval_groups = audio.get_beat_interval_groups(beat_stats['beat_intervals'], speed_multiplier, 
                                                          speed_multiplier_offset)
    
    # Generate random video segments according to beat intervals
    video_segments, rejected_segments = video.generate_video_segments(video_files, beat_interval_groups)

    # Save reusable spec for the music video
    spec = v_io.save_music_video_spec(audio_file, video_files, speed_multiplier, 
                                      speed_multiplier_offset, beat_stats, beat_interval_groups,
                                      video_segments)

    # Compile music video from video segments and audio
    video.create_music_video(video_segments, audio_file, spec)

    # Print stats for rejected video segments
    v_util.print_rejected_segment_stats(rejected_segments)

    # Save the individual segments if asked to do so
    if save_segments:
        print("Saving video segments...")
        v_io.save_video_segments(video_segments)

    # Save the video segments that were rejected
    if save_rejected_segments:
        print("Saving rejected segments...")
        v_io.save_rejected_segments(rejected_segments)

def recreate_music_video(args):
    output_name = args.output_name
    c.music_video_crf = args.crf
    video_dimensions = args.video_dimensions
    preserve_video_dimensions = args.preserve_video_dimensions
    c.allow_repeats = args.allow_repeats
    save_segments = args.save_segments
    spec_src = args.spec_src
    replace_segments = args.replace_segments

    # Prepare Inputs
    music_video_name = output_name if output_name else clu.get_music_video_name(True)
    spec_file = spec_src if spec_src else clu.prompt_file_selection(c.FileType.SPEC)
    spec = util.parse_spec_file(spec_file)
    if replace_segments:
        clu.validate_replace_segments(replace_segments, spec['video_segments'])
    video_files = [video_file['file_path'] for video_file in spec['video_files']]
    audio_src = spec['audio_file']['file_path']
    audio_offset = spec['audio_file']['offset']
    audio_file = audio_src if audio_src else clu.prompt_file_selection(c.FileType.AUDIO)
    
    # Reserve file for music video
    v_util.reserve_music_video_file(music_video_name)

    # Set dimensions for music video
    if not preserve_video_dimensions:
        c.music_video_dimensions = video_dimensions if video_dimensions \
                                   else v_sizing.largest_dimensions_with_aspect_ratio(video_files)

    # Offset the audio if specified in spec
    if audio_offset and audio_offset > 0:
        print("Creating temporary audio file with specified offset {}...".format(audio_offset))
        audio_file = audio.create_temp_offset_audio_file(audio_file, audio_offset)

    # Regenerate the video segments from the spec file
    regen_video_segments = video.regenerate_video_segments(spec, replace_segments)

    # Save regenerated spec for the music video
    regenerated_spec = v_io.save_regenerated_music_video_spec(spec, regen_video_segments)

    # Compile music video from video segments and audio
    video.create_music_video(regen_video_segments, audio_file, regenerated_spec)

    # Save the individual segments if asked to do so
    if save_segments:
        print("Saving video segments...")
        v_io.save_video_segments(regen_video_segments)

def preview_audio(args):
    audio_src = args.audio_src
    speed_multiplier = args.speed_multiplier
    speed_multiplier_offset = args.speed_multiplier_offset

    print("Creating audio preview...")

    # Prepare Inputs
    audio_file = audio_src if audio_src else clu.prompt_file_selection(c.FileType.AUDIO)

    # Get beat intervals & other stats from audio file
    beat_stats = audio.get_beat_stats(audio_file)

    # Assign beat intervals to groups based on speed_multiplier
    beat_interval_groups = audio.get_beat_interval_groups(beat_stats['beat_intervals'], speed_multiplier, 
                                                          speed_multiplier_offset)

    # Prepare preview beat locations
    preview_beat_locations = audio.flatten_beat_interval_groups(beat_interval_groups)

    # Create preview audio file
    audio.preview_audio_beats(audio_file, preview_beat_locations)

def exit_handler():
    # Cleanup reserved music video folder if empty
    if c.music_video_name:
        reserved_music_video_file = paths.music_video_output_path(c.music_video_name)
        if os.path.exists(reserved_music_video_file) and os.stat(reserved_music_video_file).st_size == 0:
            os.remove(reserved_music_video_file)

def setup():
    # Configuration
    c.debug = args.debug
    if c.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    atexit.register(exit_handler)

    # Make sure output folder is created
    util.ensure_dir(paths.OUTPUT_PATH_BASE)

def prepare_args(args):
    """
    Formats and validates program inputs
    """
    clu.validate_path(*[args.audio_src, args.video_src, args.spec_src])

    args.video_dimensions = tuple(args.video_dimensions) if args.video_dimensions else None
    if args.speed_multiplier:
        clu.validate_speed_multiplier(args.speed_multiplier, args.speed_multiplier_offset)

    return args

def parse_args(args):
    parser = argparse.ArgumentParser()
    common_parser = argparse.ArgumentParser(add_help=False)
    video_parser = argparse.ArgumentParser(add_help=False) 
    audio_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    """ SHARED PARAMETERS """

    # Common Parameters
    common_parser.add_argument('-db', '--debug', dest='debug', action='store_true', default=False, help='Pass in this argument to print useful debug info.')

    # Video Common Parameters
    video_parser.add_argument('-o', '--output-name', dest='output_name', help='The name for the music video. Otherwise will output ' + c.MUSIC_VIDEO_NAME_DEFAULT + '_0' + c.VIDEO_OUTPUT_EXTENSION + ', ' + c.MUSIC_VIDEO_NAME_DEFAULT + '_1' + c.VIDEO_OUTPUT_EXTENSION + ', etc...')
    video_parser.add_argument('-crf', '--crf', dest='crf', type=int, default=c.DEFAULT_VIDEO_CRF, help='The crf quality value for the music video. Takes an integer from 0 (lossless) to 51 (lossy). Defaults to 18.')
    video_parser.add_argument('-vd', '--video-dimensions', dest='video_dimensions', type=int, nargs=2, help='Pass in this argument to manually set the pixel dimensions for the music video, width and height. All video segments will be resized (cropped and/or scaled) appropriately to match these dimensions. Otherwise, the best dimensions for the music video are calculated automatically. Takes width then height integer values separated by spaces e.g., 1920 1080')
    video_parser.add_argument('-pvd', '--preserve-video-dimensions', dest='preserve_video_dimensions', action='store_true', default=False, help='Pass in this argument to preserve the various screen dimensions of the videos, and not perform any resizing.')
    video_parser.add_argument('-ar', '--allow-repeats', dest='allow_repeats', action='store_true', default=False, help='Pass in this argument to allow repeat segments in the music video (segments that overlap in any way).')
    video_parser.add_argument('-ss', '--save-segments', dest='save_segments', action='store_true', default=False, help='Pass in this argument to save all the individual segments that compose the music video.')

    # Audio Common Parameters
    audio_parser.add_argument('-a', '--audio-source', dest='audio_src', help='The audio file for the music video. Supports any audio format supported by ffmpeg, such as wav, aiff, flac, ogg, mp3, etc...')
    audio_parser.add_argument('-sm', '--speed-multiplier', dest='speed_multiplier', type=Fraction, default=1, help='Pass in this argument to speed up or slow down the scene changes in the music video. Should be of the form x or 1/x, where x is a natural number. (e.g.) 2 for double speed, or 1/2 for half speed.')
    audio_parser.add_argument('-smo', '--speed-multiplier-offset', dest='speed_multiplier_offset', type=int, help='Pass in this argument alongside a slowdown speed multiplier to offset the grouping of beat intervals by a specified amount. Takes an integer, with a max offset of x - 1 for a slowdown of 1/x.')

    """ COMMANDS """
 
    # Create Command Parameters
    create_parser = subparsers.add_parser('create', parents = [common_parser, audio_parser, video_parser], help="Create a new music video.")
    create_parser.set_defaults(func=create_music_video)
    create_parser.add_argument('-v', '--video-source', dest='video_src', nargs='+', help='The video(s) for the music video. Takes a list of files and folders separated by spaces. Supports any video format supported by ffmpeg, such as .ogv, .mp4, .mpeg, .avi, .mov, etc...')
    create_parser.add_argument('-sx', '--save-rejected-segments', dest='save_rejected_segments', action='store_true', default=False, help='Pass in this argument to save all segments that were rejected from the music video.')

    # Recreate Command Parameters
    recreate_parser = subparsers.add_parser('recreate', parents = [common_parser, video_parser], help="Recreate a music video from a spec file.")
    recreate_parser.set_defaults(func=recreate_music_video)
    recreate_parser.add_argument('-s', '--spec-source', dest='spec_src', help='The spec file from which to recreate the music video. Spec files are generated alongside music videos created by this program.')
    recreate_parser.add_argument('-rs', '--replace-segments', dest='replace_segments', type=int, nargs='+', help='Pass in this argument to provide a list of segment numbers in the music video to replace with new random segments. Takes values separated by spaces (e.g.) 98 171 200 305.')

    # Preview Command Parameters
    preview_parser = subparsers.add_parser('preview', parents = [common_parser, audio_parser], help="Create an audio preview of scene change locations for a music video by marking the audio with beeps.")
    preview_parser.set_defaults(func=preview_audio)

    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    args = prepare_args(args)
    setup(args)
    args.func(args)

    print("All Done!")


