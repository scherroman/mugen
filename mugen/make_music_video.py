import os
import sys
import atexit
import logging
import argparse
from fractions import Fraction

# Add base project module to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Project modules
import mugen.audio as audio
from mugen.video import video, sizing
import mugen.utility as util
import mugen.settings as s

def create_music_video(args):
    output_name = args.output_name
    video_dimensions = (args.video_dimensions[0], args.video_dimensions[0]) if args.video_dimensions else None
    preserve_video_dimensions = args.preserve_video_dimensions
    save_segments = args.save_segments
    save_rejected_segments = args.save_rejected_segments

    audio_src = args.audio_src
    video_src = args.video_src if args.video_src else []
    speed_multiplier = args.speed_multiplier
    speed_multiplier_offset = args.speed_multiplier_offset

    # Prepare Inputs
    output_name = util.sanitize_filename(output_name)
    s.music_video_name = util.get_music_video_name(output_name, False)
    speed_multiplier, speed_multiplier_offset = util.parse_speed_multiplier(speed_multiplier, speed_multiplier_offset)
    audio_file = util.get_file(s.FILE_TYPE_AUDIO, audio_src)
    video_files = util.get_files(s.FILE_TYPE_VIDEO, *video_src)

    # Reserve file for music video
    video.reserve_music_video_file(s.music_video_name)

    # Set dimensions for music video
    if not preserve_video_dimensions:
        s.music_video_dimensions = video_dimensions if video_dimensions \
                                   else sizing.get_music_video_dimensions(video_files)

    # Get beat intervals & other stats from audio file
    beat_stats = audio.get_beat_stats(audio_file)

    # Assign beat intervals to groups based on speed_multiplier
    beat_interval_groups = audio.get_beat_interval_groups(beat_stats['beat_intervals'], speed_multiplier, 
                                                          speed_multiplier_offset)
    
    # Generate random video segments according to beat intervals
    video_segments, rejected_segments = video.generate_video_segments(video_files, beat_interval_groups)

    # Save reusable spec for the music video
    video.save_music_video_spec(audio_file, video_files, speed_multiplier, 
                                speed_multiplier_offset, beat_stats, beat_interval_groups, 
                                video_segments)

    # Compile music video from video segments and audio
    video.create_music_video(video_segments, audio_file)

    # Print stats for rejected video segments
    video.print_rejected_segment_stats(rejected_segments)

    # Save the individual segments if asked to do so
    if save_segments:
        video.save_video_segments(video_segments)

    # Save the video segments that were rejected if in debug mode
    if save_rejected_segments:
        video.save_rejected_segments(rejected_segments)

def recreate_music_video(args):
    output_name = args.output_name
    video_dimensions = args.video_dimensions
    preserve_video_dimensions = args.preserve_video_dimensions if args.video_dimensions else None
    save_segments = args.save_segments
    spec_src = args.spec_src
    replace_segments = args.replace_segments

    # Prepare Inputs
    output_name = util.sanitize_filename(output_name)
    s.music_video_name = util.get_music_video_name(output_name, True)
    spec_file = util.get_file(s.FILE_TYPE_SPEC, spec_src)
    spec = util.parse_spec_file(spec_file)
    video_files = [video_file['file_path'] for video_file in spec['video_files']]
    audio_file = spec['audio_file']['file_path']
    audio_offset = spec['audio_file']['offset']

    # Reserve file for music video
    video.reserve_music_video_file(s.music_video_name)

    # Set dimensions for music video
    s.music_video_dimensions = video_dimensions if video_dimensions \
                               else sizing.get_music_video_dimensions(video_files)

    # Offset the audio if specified in spec
    if audio_offset and audio_offset > 0:
        audio_file = audio.get_temp_offset_audio_file(audio_file, audio_offset)

    # Regenerate the video segments from the spec file
    regen_video_segments = video.regenerate_video_segments(spec, replace_segments)

    # Save regenerated spec for the music video
    video.save_regenerated_music_video_spec(spec, regen_video_segments)

    # Compile music video from video segments and audio
    video.create_music_video(regen_video_segments, audio_file)

    # Save the individual segments if asked to do so
    if save_segments:
        video.save_video_segments(regen_video_segments)

def exit_handler():
    # Cleanup reserved music video file if empty
    if s.music_video_name:
        reserved_music_video_file = util.get_output_path(s.music_video_name)
        if os.path.exists(reserved_music_video_file) and os.stat(reserved_music_video_file).st_size == 0:
            os.remove(reserved_music_video_file)
    # Cleanup temp folder
    util.delete_dir(s.TEMP_PATH_BASE)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parent_parser = argparse.ArgumentParser(add_help=False) 
    subparsers = parser.add_subparsers()

    # Common Parameters
    parent_parser.add_argument('-o', '--output-name', dest='output_name', help='The name for the music video. Otherwise will output music_video_0' + s.OUTPUT_EXTENSION + ', music_video_1' + s.OUTPUT_EXTENSION + ', etc...')
    parent_parser.add_argument('-vd', '--video-dimensions', dest='video_dimensions', type=int, nargs=2, help='Pass in this argument to manuualy set the pixel dimensions for the music video, width and height. All video segments will be resized (cropped and/or scaled) appropriately to match these dimensions. Otherwise, the best dimensions for the music video are calculated automatically. Takes width then height integer values separated by spaces e.g., 1920 1080')
    parent_parser.add_argument('-pvd', '--preserve-video-dimensions', dest='preserve_video_dimensions', action='store_true', default=False, help='Pass in this argument to preserve the various screen dimensions of the videos, and not perform any resizing.')
    parent_parser.add_argument('-ss', '--save-segments', dest='save_segments', action='store_true', default=False, help='Pass in this argument to save all the individual segments that compose the music video.')
    parent_parser.add_argument('-db', '--debug', dest='debug', action='store_true', default=False, help='Pass in this argument to print useful debug info and save all rejected segments.')
    
    # Create Command Parameters
    create_parser = subparsers.add_parser('create', parents = [parent_parser])
    create_parser.set_defaults(func=create_music_video)
    create_parser.add_argument('-a', '--audio-source', dest='audio_src', help='The audio file for the music video. Supports any audio format supported by ffmpeg, such as wav, aiff, flac, ogg, mp3, etc...')
    create_parser.add_argument('-v', '--video-source', dest='video_src', nargs='+', help='The video(s) for the music video. Takes a list of files and folders separated by spaces. Supports any video format supported by ffmpeg, such as .ogv, .mp4, .mpeg, .avi, .mov, etc...')
    create_parser.add_argument('-sm', '--speed-multiplier', dest='speed_multiplier', type=Fraction, default=1, help='Pass in this argument to speed up or slow down the scene changes in the music video. Should be of the form x or 1/x, where x is a natural number. (e.g.) 2 for double speed, or 1/2 for half speed.')
    create_parser.add_argument('-smo', '--speed-multiplier-offset', dest='speed_multiplier_offset', type=int, help='Pass in this argument alongside a slowdown speed multiplier to offset the grouping of beat intervals by a specified amount. Takes an integer, with a max offset of x - 1 for a slowdown of 1/x.')
    create_parser.add_argument('-sx', '--save-rejected-segments', dest='save_rejected_segments', action='store_true', default=False, help='Pass in this argument to save all segments that were rejected from the music video.')

    # Recreate Command Parameters
    recreate_parser = subparsers.add_parser('recreate', parents = [parent_parser])
    recreate_parser.set_defaults(func=recreate_music_video)
    recreate_parser.add_argument('-s', '--spec-source', dest='spec_src', help='The spec file from which to recreate the music video. Spec files are generated alongside music videos created by this program.')
    recreate_parser.add_argument('-rs', '--replace-segments', dest='replace_segments', type=int, nargs='+', help='Pass in this argument to provide a list of segment numbers in the music video to replace with new random segments. Takes values separated by spaces (e.g.) 98 171 200 305.')

    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    s.debug = args.debug
    
    # Configuration
    if s.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    atexit.register(exit_handler)

    args.func(args)

    print("All Done!")


