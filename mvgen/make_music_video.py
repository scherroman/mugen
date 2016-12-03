import os
import sys
import json
import shutil
import random
import logging
import argparse
import Tkinter as tk
import tkFileDialog
from tqdm import tqdm
from collections import OrderedDict
from fractions import Fraction

import tesserocr
import essentia
import essentia.standard
from moviepy.editor import *
from moviepy.video.tools.cuts import detect_scenes
from PIL import Image

# Globals
debug = False
music_video_name = None

# Utility constants
MOVIEPY_FPS = 24
MOVIEPY_CODEC = 'libx264'
MOVIEPY_AUDIO_BITRATE = '320K'

MIN_EXTREMA_RANGE = 30
DURATION_PRECISION = 17

RS_TYPE_SCENE_CHANGE = 'scene_change'
RS_TYPE_TEXT_DETECTED = 'text_detected'
RS_TYPE_SOLID_COLOR = 'solid_color'

# Path constants
OUTPUT_PATH_BASE = 'output/'
OUTPUT_NAME = 'music_video'
OUTPUT_EXTENSION = '.mp4'
SPEC_EXTENSION = '.json'

SEGMENTS_PATH_BASE = 'segments/'
RS_PATH_BASE = 'rejected_segments/'
RS_PATH_SCENE_CHANGE = RS_PATH_BASE + RS_TYPE_SCENE_CHANGE + '/'
RS_PATH_TEXT_DETECTED = RS_PATH_BASE + RS_TYPE_TEXT_DETECTED + '/'
RS_PATH_SOLID_COLOR = RS_PATH_BASE + RS_TYPE_SOLID_COLOR +'/'

# PRIMARY METHODS

# Extracts beat locations and intervals from an audio file
def get_beat_stats(audio_file):
	print("Processing audio beat patterns...")

	# Load audio
	try:
		loader = essentia.standard.MonoLoader(filename = audio_file)
	except Exception as e:
		print(e)
		sys.exit(1)
	
	# Get beat stats from audio
	audio = loader()
	rhythm_loader = essentia.standard.RhythmExtractor2013()
	rhythm = rhythm_loader(audio)
	beat_stats = {'bpm':rhythm[0], 
				  'beat_locations':rhythm[1], 
				  'bpm_estimates':rhythm[3], 
				  'beat_intervals':rhythm[4]}

	logging.debug("\n")
	logging.debug("Beats per minute: {}".format(beat_stats['bpm']))
	logging.debug("Beat locations: {}".format(beat_stats['beat_locations'].tolist()))
	logging.debug("Beat intervals: {}".format(beat_stats['beat_intervals'].tolist()))
	logging.debug("BPM estimates: {}".format(beat_stats['bpm_estimates'].tolist()))
	logging.debug("\n")

	return beat_stats

# Generates a set of random video segments from the video files
# with durations corresponding to the durations of the beat intervals
def get_video_segments(video_files, beat_interval_groups, speed_multiplier):
	# Remove improper video files from video_files
	videos = []
	for video_file in video_files:
		video = None
		try:
			video = VideoFileClip(video_file).without_audio()
		except Exception as e:
			print("Error reading video file '{}'. Will be excluded from the music video.".format(video_file))
			continue
		else:
			video.src_file = video_file
			videos.append(video)

	# If no video files to work with, exit
	if len(videos) == 0:
		print("No more video files left to work with. I can't continue :(")
		sys.exit(1)

	print("Grabbing random video segments from {} videos according to beat patterns...".format(len(videos)))

	# Extract video segments from videos
	video_segments = []
	rejected_segments = [] 
	for beat_interval_group in tqdm(beat_interval_groups):
		for interval in beat_interval_group['intervals']:
			video_segment, new_rejected_segments = generate_video_segment(videos, interval)

			# Add metadata for music video spec
			video_segment.sequence_number = len(video_segments)
			video_segment.beat_interval_numbers = beat_interval_group['beat_interval_numbers']
			
			video_segments.append(video_segment)
			rejected_segments.extend(new_rejected_segments)
	
	return video_segments, rejected_segments

def generate_video_segment(videos, duration):
	video_segment = None
	rejected_segments = []
	while video_segment == None:
		random_video_number = random.randint(0, len(videos) - 1)
		random_video = videos[random_video_number]
		start_time = round(random.uniform(0, random_video.duration - duration), DURATION_PRECISION)
		end_time = start_time + round(duration, DURATION_PRECISION)

		video_segment = random_video.subclip(start_time,end_time)
		# Add metadata for music video spec
		video_segment.src_video_file = random_video.src_file
		video_segment.src_start_time = start_time
		video_segment.src_end_time = end_time

		# Discard video segment if there is a scene change
		reject_type = None
		if segment_contains_scene_change(video_segment):
			reject_type = RS_TYPE_SCENE_CHANGE
		# Discard video segment if there is any detectable text
		elif segment_contains_text(video_segment):
			reject_type = RS_TYPE_TEXT_DETECTED
		# Discard video segment if it contains a solid color
		elif segment_has_solid_color(video_segment):
			reject_type = RS_TYPE_SOLID_COLOR

		if reject_type:
			rejected_segments.append({'reject_type':reject_type, 'video_segment': video_segment})
			video_segment = None

	return video_segment, rejected_segments

# Group together beat intervals based on speed_multiplier by
# -> splitting individual beat intervals for speedup
# -> combining adjacent beat intervals for slowdown
# -> using original beat interval for normal speed
def get_beat_interval_groups(beat_intervals, speed_multiplier):
	beat_interval_groups = [] 
	beat_intervals = beat_intervals.tolist()
	
	beat_intervals_covered = 0
	for index, beat_interval in enumerate(beat_intervals):
		if index < beat_intervals_covered:
			continue

		beat_interval_group = None

		if speed_multiplier < 1:
			desired_num_intervals = speed_multiplier.denominator
			remaining_intervals = len(beat_intervals) - index
			if remaining_intervals < desired_num_intervals:
				desired_num_intervals = remaining_intervals

			interval_combo = sum(beat_intervals[index:index + desired_num_intervals])
			interval_combo_numbers = range(index, index + desired_num_intervals)
			beat_interval_group = {'intervals':[interval_combo], 'beat_interval_numbers':interval_combo_numbers}

			beat_intervals_covered += desired_num_intervals
		elif speed_multiplier > 1:
			speedup_factor = speed_multiplier.numerator
			interval_splinter = beat_interval/speedup_factor
			interval_splinters = [interval_splinter] * speedup_factor
			beat_interval_group = {'intervals':interval_splinters, 'beat_interval_numbers':index}
			beat_intervals_covered += 1
		else:
			beat_interval_group = {'intervals':[beat_interval], 'beat_interval_numbers':index}
			beat_intervals_covered += 1

		beat_interval_groups.append(beat_interval_group)

	logging.debug("\nbeat_interval_groups: {}\n".format(beat_interval_groups))

	return beat_interval_groups

# Compile music video from video segments and audio
def create_music_video(video_segments, audio_file):
	print("Generating music video from video segments and audio...")

	# Make sure output directory exists
	ensure_dir(OUTPUT_PATH_BASE)
	
	# Get output path for file
	output_path = get_output_path(music_video_name)

	audio = AudioFileClip(audio_file)
	music_video = concatenate_videoclips(video_segments, method="compose")
	music_video = music_video.set_audio(audio)
	music_video.write_videofile(output_path, fps=MOVIEPY_FPS, codec=MOVIEPY_CODEC, audio_bitrate=MOVIEPY_AUDIO_BITRATE)

# Save the individual segments that compose the music video
def save_video_segments(video_segments):
	print("Saving video segments...")

	# Create music video's segments directory (overwrite if exists)
	segments_dir = get_segments_dir(music_video_name)
	recreate_dir(segments_dir)

	count = 0
	for video_segment in video_segments:
		segment_path = segments_dir + "%s" % count + OUTPUT_EXTENSION
		video_segment.write_videofile(segment_path, fps=MOVIEPY_FPS, codec=MOVIEPY_CODEC)
		count += 1

# Save the video segments that were rejected
def save_rejected_segments(rejected_segments):
	print("Saving rejected segments...")

	# Create rejected segments directories (overwrite if exists)
	recreate_dir(*[RS_PATH_BASE, RS_PATH_SCENE_CHANGE,RS_PATH_TEXT_DETECTED, RS_PATH_SOLID_COLOR])

	rs_scene_change_count = 0
	rs_text_detected_count = 0
	rs_solid_color_count = 0
	for rejected_segment in rejected_segments:
		reject_type = rejected_segment['reject_type']
		video_segment = rejected_segment['video_segment']

		if reject_type == RS_TYPE_SCENE_CHANGE:
			segment_path = RS_PATH_SCENE_CHANGE + "%s" % rs_scene_change_count + OUTPUT_EXTENSION
			video_segment.write_videofile(segment_path, fps=MOVIEPY_FPS, codec=MOVIEPY_CODEC)
			rs_scene_change_count += 1
		elif reject_type == RS_TYPE_TEXT_DETECTED:
			segment_path = RS_PATH_TEXT_DETECTED + "%s" % rs_text_detected_count + OUTPUT_EXTENSION
			video_segment.write_videofile(segment_path, fps=MOVIEPY_FPS, codec=MOVIEPY_CODEC)
			rs_text_detected_count += 1
		else:
			segment_path = RS_PATH_SOLID_COLOR + "%s" % rs_solid_color_count + OUTPUT_EXTENSION
			video_segment.write_videofile(segment_path, fps=MOVIEPY_FPS, codec=MOVIEPY_CODEC)
			rs_solid_color_count += 1

# Save reusable spec for the music video
def save_music_video_spec(audio_file, video_files, speed_multiplier, beat_stats, beat_interval_groups, video_segments):
	print("Saving music video spec...")

	spec = OrderedDict([('audio_file', audio_file), 
						('video_files', video_files),
						('speed_multiplier', float(speed_multiplier)),
						('beats_per_minute', beat_stats['bpm']),
						('beat_locations', beat_stats['beat_locations'].tolist()),
						('beat_intervals', beat_stats['beat_intervals'].tolist()),
						('bpm_estimates', beat_stats['bpm_estimates'].tolist()),
						('beat_interval_groups', beat_interval_groups),
						('video_segments', [])])

	for video_segment in video_segments:
		segment_spec = OrderedDict([('sequence_number', video_segment.sequence_number),
									('beat_interval_numbers', video_segment.beat_interval_numbers),
									('duration', video_segment.duration), 
									('src_video_file', video_segment.src_video_file),
									('src_start_time', video_segment.src_start_time),
									('src_end_time', video_segment.src_end_time)])

		spec['video_segments'].append(segment_spec)

	spec_path = get_spec_path(music_video_name)
	with open(spec_path, 'w') as outfile:
		json.dump(spec, outfile, indent=2, ensure_ascii=False)

# HELPER METHODS

def print_rejected_segment_stats(rejected_segments):
	print("# rejected segments with scene changes: {}".format(len([seg for seg in rejected_segments if seg['reject_type'] == RS_TYPE_SCENE_CHANGE])))
	print("# rejected segments with text detected: {}".format(len([seg for seg in rejected_segments if seg['reject_type'] == RS_TYPE_TEXT_DETECTED])))
	print("# rejected segments with solid colors: {}".format(len([seg for seg in rejected_segments if seg['reject_type'] == RS_TYPE_SOLID_COLOR])))

def segment_contains_scene_change(video_segment):
	cuts, luminosities = detect_scenes(video_segment, fps=MOVIEPY_FPS, progress_bar=False)

	return True if len(cuts) > 1 else False
		
def segment_contains_text(video_segment):
	first_frame_contains_text = False
	last_frame_contains_text = False
	first_frame = video_segment.get_frame(t='00:00:00')
	last_frame = video_segment.get_frame(t=video_segment.duration)

	#Check first frame
	frame_image = Image.fromarray(first_frame)
	text = tesserocr.image_to_text(frame_image)
	if (len(text.strip()) > 0):
		first_frame_contains_text = True

	#Check last frame
	frame_image = Image.fromarray(last_frame)
	text = tesserocr.image_to_text(frame_image)
	if (len(text.strip()) > 0):
		last_frame_contains_text = True

	return True if first_frame_contains_text or last_frame_contains_text else False

def segment_has_solid_color(video_segment):
	first_frame_is_solid_color = False
	last_frame_is_solid_color = False
	first_frame = video_segment.get_frame(t='00:00:00')
	last_frame = video_segment.get_frame(t=video_segment.duration)

	#Check first frame
	frame_image = Image.fromarray(first_frame)
	extrema = frame_image.convert("L").getextrema()
	if abs(extrema[1] - extrema[0]) <= MIN_EXTREMA_RANGE:
		first_frame_is_solid_color = True

	#Check last frame
	frame_image = Image.fromarray(last_frame)
	extrema = frame_image.convert("L").getextrema()
	if abs(extrema[1] - extrema[0]) <= MIN_EXTREMA_RANGE:
		last_frame_is_solid_color = True

	return True if first_frame_is_solid_color or last_frame_is_solid_color else False

# Returns an audio file path from an audio source, or after prompting user for selection
def get_audio_file(audio_src):
	audio_file = None

	# Select audio via terminal input
	if audio_src:
		audio_src_exists = os.path.exists(audio_src)

		# Check that audio file exists
		if not audio_src_exists:
			print("Audio source path '{}' does not exist.".format(audio_src))
			sys.exit(1)

		audio_file = audio_src
	# Select audio via file selection dialog
	else:
		root = tk.Tk()
		root.withdraw()
		audio_src = tkFileDialog.askopenfilename(message="Select audio file")
		root.update()

		if audio_src == "":
			print("No audio file was selected.".format(audio_src))
			sys.exit(1)

		# Properly encode file name
		audio_file = audio_src.encode('utf-8')

	logging.debug("audio_file {}".format(audio_file))
	return audio_file

# Returns list of video file paths from a video source, or after prompting user for selection
def get_video_files(video_src):
	video_files = []

	# Select videos via terminal input
	if video_src:
		video_src_exists = os.path.exists(video_src)
		video_src_is_dir = os.path.isdir(video_src)

		# Check that video file/directory exists
		if not video_src_exists:
			print("Video source path {} does not exist.".format(video_src))
			sys.exit(1)

		# Check if video source is file or directory	
		if video_src_is_dir:
			video_files = [file for file in listdir_nohidden(video_src) if os.path.isfile(file)]
		else:
			video_files = [video_src]
	# Select videos via file selection dialog
	else:
		root = tk.Tk()
		root.withdraw()
		video_src = tkFileDialog.askopenfilename(message="Select video file(s)", multiple=True)
		root.update()

		if video_src == "":
			print("No video file(s) were selected.".format(video_src))
			sys.exit(1)

		# Properly encode file names
		video_files = [video_file.encode('utf-8') for video_file in video_src]

	logging.debug("video_src {}".format(video_src))
	for video_file in video_files:
		logging.debug("video_file: {}".format(video_file))
	return video_files

def parse_speed_multiplier(speed_multiplier):
	try:
		speed_multiplier = Fraction(speed_multiplier)
	except (ValueError, ZeroDivisionError) as e:
		print("Improper speed multiplier provided. Please check supported values on the help menu via --help")
		sys.exit(1)
	else:
		if speed_multiplier == 0 or (speed_multiplier.numerator != 1 and speed_multiplier.denominator != 1):
			print("Improper speed multiplier provided. Please check supported values on the help menu via --help")
			sys.exit(1)

	logging.debug('speed_multiplier: {}'.format(speed_multiplier))

	return speed_multiplier

def ensure_dir(*directories):
	for directory in directories:
		if not os.path.exists(directory):
			os.makedirs(directory)

def recreate_dir(*directories):
	for directory in directories:
		if os.path.exists(directory):
			shutil.rmtree(directory)
		os.makedirs(directory)

def get_output_path(music_video_name):
	return OUTPUT_PATH_BASE + music_video_name + OUTPUT_EXTENSION

def get_spec_path(music_video_name):
	return OUTPUT_PATH_BASE + music_video_name + '_spec' + SPEC_EXTENSION

def get_segments_dir(music_video_name):
	return SEGMENTS_PATH_BASE + music_video_name + '/'

def get_music_video_name(output_name):
	if output_name == None:
		count = 0
		while os.path.exists(OUTPUT_PATH_BASE + OUTPUT_NAME + "_%s" % count + OUTPUT_EXTENSION):
			count += 1
		return OUTPUT_NAME + "_%s" % count
	else:
		return output_name

def listdir_nohidden(path):
    for file in os.listdir(path):
        if not file.startswith('.'):
            yield path + file

# MAIN

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--audio-source', dest='audio_src', help='The audio file for the music video. Supports any audio format supported by ffmpeg, such as wav, aiff, flac, ogg, mp3, etc...')
	parser.add_argument('-v', '--video-source', dest='video_src', help='The video(s) for the music video. Either a singular video file or a folder containing multiple video files. Supports any video format supported by ffmpeg, such as .ogv, .mp4, .mpeg, .avi, .mov, etc...')
	parser.add_argument('-o', '--output-name', dest='output_name', help='The name for the music video. Otherwise will output music_video_0' + OUTPUT_EXTENSION + ', music_video_1' + OUTPUT_EXTENSION + ', etc...')
	parser.add_argument('-s', '--speed-multiplier', dest='speed_multiplier', default=1, help='Pass in this argument to speed up or slow down the scene changes in the music video. Should be of the form x or 1/x, where x is a natural number. e.g. 2 for double speed, or 1/2 for half speed.')
	parser.add_argument('-ss', '--save-segments', dest='save_segments', action='store_true', default=False, help='Pass in this argument to save all the individual segments that compose the music video.')
	parser.add_argument('-db', '--debug', dest='debug', action='store_true', default=False, help='Pass in this argument to print debug statements and save all rejected segments.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	audio_src = args.audio_src
	video_src = args.video_src
	output_name = args.output_name
	speed_multiplier = args.speed_multiplier
	save_segments = args.save_segments
	debug = args.debug
	
	# Setup debug logging
	if debug:
		logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

	speed_multiplier = parse_speed_multiplier(speed_multiplier)
	music_video_name = get_music_video_name(output_name)
	audio_file = get_audio_file(audio_src)
	video_files = get_video_files(video_src)
	
	# Get beat locations and intervals from audio file
	beat_stats = get_beat_stats(audio_file)

	# Assign beat intervals to groups based on speed_multiplier
	beat_interval_groups = get_beat_interval_groups(beat_stats['beat_intervals'], speed_multiplier)
	
	# Generate random video segments according to beat intervals
	video_segments, rejected_segments = get_video_segments(video_files, beat_interval_groups, speed_multiplier)

	# Save reusable spec for the music video
	save_music_video_spec(audio_file, video_files, speed_multiplier, beat_stats, beat_interval_groups, video_segments)

	# Compile music video from video segments and audio
	create_music_video(video_segments, audio_file)

	# Print stats for rejected video segments
	print_rejected_segment_stats(rejected_segments)

	# Save the individual segments if asked to do so
	if save_segments:
		save_video_segments(video_segments)

	# Save the video segments that were rejected if in debug mode
	if debug:
		save_rejected_segments(rejected_segments)


