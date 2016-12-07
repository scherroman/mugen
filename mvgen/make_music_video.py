import os
import sys
import atexit
import logging
import argparse

# Project modules
import audio
import video
import utility as util
import settings as s

def exit_handler():
	# Cleanup reserved music video file if empty
	if s.music_video_name:
		reserved_music_video_file = util.get_output_path(s.music_video_name)
		if os.path.exists(reserved_music_video_file) and os.stat(reserved_music_video_file).st_size == 0:
			os.remove(reserved_music_video_file)

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--audio-source', dest='audio_src', help='The audio file for the music video. Supports any audio format supported by ffmpeg, such as wav, aiff, flac, ogg, mp3, etc...')
	parser.add_argument('-v', '--video-source', dest='video_src', help='The video(s) for the music video. Either a singular video file or a folder containing multiple video files. Supports any video format supported by ffmpeg, such as .ogv, .mp4, .mpeg, .avi, .mov, etc...')
	parser.add_argument('-o', '--output-name', dest='output_name', help='The name for the music video. Otherwise will output music_video_0' + s.OUTPUT_EXTENSION + ', music_video_1' + s.OUTPUT_EXTENSION + ', etc...')
	parser.add_argument('-sm', '--speed-multiplier', dest='speed_multiplier', default=1, help='Pass in this argument to speed up or slow down the scene changes in the music video. Should be of the form x or 1/x, where x is a natural number. e.g. 2 for double speed, or 1/2 for half speed.')
	parser.add_argument('-smo', '--speed-multiplier-offset', dest='speed_multiplier_offset', help='Pass in this argument alongside a slowdown speed multiplier to offset the grouping of beat intervals by a specified amount. Takes an integer, with a max offset of x - 1 for a slowdown of 1/x.')
	parser.add_argument('-ss', '--save-segments', dest='save_segments', action='store_true', default=False, help='Pass in this argument to save all the individual segments that compose the music video.')
	parser.add_argument('-db', '--debug', dest='debug', action='store_true', default=False, help='Pass in this argument to print debug statements and save all rejected segments.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	audio_src = args.audio_src
	video_src = args.video_src
	output_name = args.output_name
	speed_multiplier = args.speed_multiplier
	speed_multiplier_offset = args.speed_multiplier_offset
	save_segments = args.save_segments
	s.debug = args.debug
	
	# Configuration
	if s.debug:
		logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
	atexit.register(exit_handler)

	# Prepare Inputs
	output_name = util.sanitize_filename(output_name)
	s.music_video_name = util.get_music_video_name(output_name)
	speed_multiplier, speed_multiplier_offset = util.parse_speed_multiplier(speed_multiplier, speed_multiplier_offset)
	audio_file = util.get_audio_file(audio_src)
	video_files = util.get_video_files(video_src)

	# Reserve music video output path
	util.reserve_file(util.get_output_path(s.music_video_name))

	# Get beat intervals & other stats from audio file
	beat_stats = audio.get_beat_stats(audio_file)

	# Assign beat intervals to groups based on speed_multiplier
	beat_interval_groups = audio.get_beat_interval_groups(beat_stats['beat_intervals'], speed_multiplier, speed_multiplier_offset)
	
	# Generate random video segments according to beat intervals
	video_segments, rejected_segments = video.get_video_segments(video_files, beat_interval_groups)

	# Save reusable spec for the music video
	video.save_music_video_spec(audio_file, video_files, speed_multiplier, speed_multiplier_offset, beat_stats, beat_interval_groups, video_segments)

	# Compile music video from video segments and audio
	video.create_music_video(video_segments, audio_file)

	# Print stats for rejected video segments
	video.print_rejected_segment_stats(rejected_segments)

	# Save the individual segments if asked to do so
	if save_segments:
		video.save_video_segments(video_segments)

	# Save the video segments that were rejected if in debug mode
	if s.debug:
		video.save_rejected_segments(rejected_segments)


