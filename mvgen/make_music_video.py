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

import tesserocr
import essentia
import essentia.standard
from moviepy.editor import *
from moviepy.video.tools.cuts import detect_scenes
from PIL import Image

debug = False
music_video_name = None

OUTPUT_PATH_BASE = 'output/'
OUTPUT_NAME = 'music_video'
OUTPUT_EXTENSION = '.mp4'
SPEC_EXTENSION = '.json'

SEGMENTS_PATH_BASE = 'segments/'
RS_PATH_BASE = 'rejected_segments/'
RS_SCENE_CHANGE = RS_PATH_BASE + 'scene_change/'
RS_TEXT_DETECTED = RS_PATH_BASE + 'text_detected/'
RS_SOLID_COLOR = RS_PATH_BASE + 'solid_color/'

# PRIMARY METHODS

# Extracts beat locations and intervals from an audio file
def get_beat_stats(audio_file):
	print("Processing audio beat patterns...")

	# Load audio
	loader = None
	try:
		loader = essentia.standard.MonoLoader(filename = audio_file)
	except Exception as e:
		print(e)
		sys.exit(1)
	audio = loader()
	
	# Get beat stats from audio
	rhythm_loader = essentia.standard.RhythmExtractor2013()
	rhythm = rhythm_loader(audio)
	beat_stats = {'bpm':rhythm[0], 
				  'beat_locations':rhythm[1], 
				  'bpm_estimates':rhythm[3], 
				  'beat_intervals':rhythm[4]}

	return beat_stats

# Generates random locations for which to segment video files 
# with lengths corresponding to the lengths of beat intervals
def get_video_segments(video_files, beat_stats):
	# Remove improper video files from video_files
	videos = []
	for video_file in video_files:
		video = None
		try:
			video = VideoFileClip(video_file).without_audio()
			video.src_file = video_file
			videos.append(video)
		except Exception as e:
			print("Error reading video file '{}'. Will be excluded from the music video.".format(video_file))
			continue

	print("Grabbing random video segments from {} videos according to beat patterns...".format(len(videos)))

	# If no video files to work with, exit
	if len(videos) == 0:
		print("No more video files left to work with. I can't continue :(")
		sys.exit(1)

	# Extract video segments from videos
	video_segments = []
	rejected_segments = {'scene_change':[], 'text_detected':[], 'solid_color':[]}
	for beat_interval in tqdm(beat_stats['beat_intervals']):
		video_segment = None
		while video_segment == None:
			random_video_number = random.randint(0, len(videos) - 1)
			random_video = videos[random_video_number]
			start_time = round(random.uniform(0, random_video.duration - beat_interval), 17)
			end_time = start_time + round(beat_interval, 17)

			video_segment = random_video.subclip(start_time,end_time)
			# Add extra metadata for music video spec
			video_segment.sequence_number = len(video_segments)
			video_segment.src_video_file = random_video.src_file
			video_segment.src_start_time = start_time
			video_segment.src_end_time = end_time

			# Discard video segment if there is a scene change
			if segment_contains_scene_change(video_segment):
				rejected_segments['scene_change'].append(video_segment)
				video_segment = None
			# Discard video segment if there is any detectable text
			elif segment_contains_text(video_segment):
				rejected_segments['text_detected'].append(video_segment)
				video_segment = None
			# Discard video segment if it contains a solid color
			elif segment_has_solid_color(video_segment):
				rejected_segments['solid_color'].append(video_segment)
				video_segment = None

		video_segments.append(video_segment)

	return video_segments, rejected_segments

# Compile music video from video segments and audio
def create_music_video(video_segments, audio_src):
	print("Generating music video from video segments and audio...")

	# Make sure output dir exists
	if not os.path.exists(OUTPUT_PATH_BASE):
		os.makedirs(OUTPUT_PATH_BASE)

	# Get output path for file
	output_path = get_output_path(music_video_name)

	audio = AudioFileClip(audio_src)
	music_video = concatenate_videoclips(video_segments, method="compose")
	music_video = music_video.set_audio(audio)
	music_video.write_videofile(output_path, fps=24, codec="libx264", audio_bitrate="320K")

# Save the individual segments that compose the music video
def save_video_segments(video_segments):
	print("Saving video segments...")

	# Create video's segments dir (overwrite if exists)
	segments_dir = get_segments_dir(music_video_name)
	if os.path.exists(segments_dir):
		shutil.rmtree(segments_dir)
	os.makedirs(segments_dir)

	count = 0
	for video_segment in video_segments:
		segment_path = segments_dir + "%s" % count + OUTPUT_EXTENSION
		video_segment.write_videofile(segment_path, fps=24, codec="libx264")
		count += 1

def save_rejected_segments(rejected_segments):
	print("Saving rejected segments...")

	if os.path.exists(RS_PATH_BASE):
		shutil.rmtree(RS_PATH_BASE)
	os.makedirs(RS_PATH_BASE)
	os.makedirs(RS_SCENE_CHANGE)
	os.makedirs(RS_TEXT_DETECTED)
	os.makedirs(RS_SOLID_COLOR)

	count = 0
	for rejected_segment in rejected_segments['scene_change']:
		segment_path = RS_SCENE_CHANGE + "%s" % count + OUTPUT_EXTENSION
		rejected_segment.write_videofile(segment_path, fps=24, codec="libx264")
		count += 1

	count = 0
	for rejected_segment in rejected_segments['text_detected']:
		segment_path = RS_TEXT_DETECTED + "%s" % count + OUTPUT_EXTENSION
		rejected_segment.write_videofile(segment_path, fps=24, codec="libx264")
		count += 1

	count = 0
	for rejected_segment in rejected_segments['solid_color']:
		segment_path = RS_SOLID_COLOR + "%s" % count + OUTPUT_EXTENSION
		rejected_segment.write_videofile(segment_path, fps=24, codec="libx264")
		count += 1

# Save reusable spec for the music video
def save_music_video_spec(audio_src, video_files, beat_stats, video_segments):
	print("Saving music video spec...")

	spec = OrderedDict([('audio_src', audio_src), 
						('video_files', video_files),
						('beats_per_minute', beat_stats['bpm']),
						('beat_locations', beat_stats['beat_locations'].tolist()),
						('beat_intervals', beat_stats['beat_intervals'].tolist()),
						('bpm_estimates', beat_stats['bpm_estimates'].tolist()),
						('video_segments', [])])

	for video_segment in video_segments:
		segment_spec = OrderedDict([('sequence_number', video_segment.sequence_number), 
									('duration', video_segment.duration), 
									('src_video_file', video_segment.src_video_file),
									('src_start_time', video_segment.src_start_time),
									('src_end_time', video_segment.src_end_time)])

		spec['video_segments'].append(segment_spec)

	spec_path = get_spec_path(music_video_name)
	with open(spec_path, 'w') as outfile:
		json.dump(spec, outfile, indent=4, ensure_ascii=False)

# HELPER METHODS

def print_rejected_segment_stats(rejected_segments):
	print("# rejected segments with scene changes: {}".format(len(rejected_segments['scene_change'])))
	print("# rejected segments with text detected: {}".format(len(rejected_segments['text_detected'])))
	print("# rejected segments with solid colors: {}".format(len(rejected_segments['solid_color'])))

def segment_contains_scene_change(video_segment):
	cuts, luminosities = detect_scenes(video_segment, fps=24, progress_bar=False)
	# print("segment {} num scenes: {}".format(len(video_segments),len(cuts)))
	if len(cuts) > 1:
		return True
	else:
		return False

def segment_contains_text(video_segment):
	#Check first frame
	frame = video_segment.get_frame(t='00:00:00')
	frame_image = Image.fromarray(frame)
	text = tesserocr.image_to_text(frame_image)
	if (len(text.strip()) > 0):
		return True
	#Check last frame
	frame = video_segment.get_frame(t=video_segment.duration)
	frame_image = Image.fromarray(frame)
	text = tesserocr.image_to_text(frame_image)
	if (len(text.strip()) > 0):
		return True

	return False

def segment_has_solid_color(video_segment):
	first_frame_is_solid_color = False
	last_frame_is_solid_color = False

	first_frame = video_segment.get_frame(t='00:00:00')
	first_frame_image = Image.fromarray(first_frame)
	extrema = first_frame_image.convert("L").getextrema()
	if abs(extrema[0] - extrema[1]) <= 10:
		first_frame_is_solid_color = True

	last_frame = video_segment.get_frame(t=video_segment.duration)
	last_frame_image = Image.fromarray(last_frame)

	extrema = last_frame_image.convert("L").getextrema()
	if abs(extrema[0] - extrema[1]) <= 10:
		last_frame_is_solid_color = True

	if first_frame_is_solid_color or last_frame_is_solid_color:
		return True
	else:
		return False
		
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
	parser.add_argument('-ss', '--save-segments', dest='save_segments', action='store_true', default=False, help='Pass in this argument to save all the individual segments that compose the music video.')
	parser.add_argument('-db', '--debug', dest='debug', action='store_true', default=False, help='Pass in this argument to print debug statements and save all rejected segments.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	audio_src = args.audio_src
	video_src = args.video_src
	output_name = args.output_name if args.output_name else None
	save_segments = args.save_segments
	debug = args.debug

	# Setup debug logging
	if debug:
		logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

	# Set global name for music video
	music_video_name = get_music_video_name(output_name)

	video_files = []

	root = tk.Tk()
	root.withdraw()
	# Select audio via terminal input
	if audio_src:
		# Read in via terminal input
		audio_src_exists = os.path.exists(audio_src)

		# Check that audio file exists
		if not audio_src_exists:
			print("Audio source path '{}' does not exist.".format(audio_src))
			sys.exit(1)
	# Select audio via file selection dialog
	else:
		audio_src = tkFileDialog.askopenfilename(message="Select audio file")
		# Properly encode file name
		audio_src = audio_src.encode('utf-8')

		if audio_src == "":
			print("No audio file was selected.".format(audio_src))
			sys.exit(1)

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
		video_src = tkFileDialog.askopenfilename(message="Select video file(s)", multiple=True)

		if video_src == "":
			print("No video file(s) were selected.".format(video_src))
			sys.exit(1)

		# Properly encode file name
		video_files = [video_file.encode('utf-8') for video_file in video_src]

	root.update()

	logging.debug("audio_src {}".format(audio_src))
	logging.debug("video_src {}".format(video_src))
	for video_file in video_files:
		logging.debug("video_file: {}".format(video_file))
	
	# Get beat locations and intervals from audio file
	beat_stats = get_beat_stats(audio_src)
	logging.debug("Beats per minute: {}".format(beat_stats['bpm']))
	logging.debug("Beat locations: {}".format(beat_stats['beat_locations']))
	logging.debug("BPM estimates: {}".format(beat_stats['bpm_estimates']))
	logging.debug("Beat intervals: {}".format(beat_stats['beat_intervals']))

	# Generate video segments according to beat intervals in audio file
	video_segments, rejected_segments = get_video_segments(video_files, beat_stats)

	# Save reusable spec for the music video
	save_music_video_spec(audio_src, video_files, beat_stats, video_segments)

	# Compile music video from video segments and audio
	create_music_video(video_segments, audio_src)

	# Print stats for rejected video segments
	print_rejected_segment_stats(rejected_segments)

	# Save the individual segments if asked to do so
	if save_segments:
		save_video_segments(video_segments)

	# Save the rejected video segments if in debug mode
	if debug:
		save_rejected_segments(rejected_segments)


