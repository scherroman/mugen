import os
import sys
import shutil
import logging
import Tkinter as tk
import tkFileDialog
from fractions import Fraction

# Project modules
import settings as s

### INPUTS ###

def get_music_video_name(output_name):
	if output_name == None:
		count = 0
		while os.path.exists(s.OUTPUT_PATH_BASE + s.OUTPUT_NAME_DEFAULT + "_%s" % count + s.OUTPUT_EXTENSION):
			count += 1
		return s.OUTPUT_NAME_DEFAULT + "_%s" % count
	else:
		return output_name

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

def parse_speed_multiplier(speed_multiplier, speed_multiplier_offset):
	try:
		speed_multiplier = Fraction(speed_multiplier)
	except (ValueError, ZeroDivisionError) as e:
		print("Improper speed multiplier provided." + s.HELP)
		sys.exit(1)
	else:
		if speed_multiplier == 0 or (speed_multiplier.numerator != 1 and speed_multiplier.denominator != 1):
			print("Improper speed multiplier provided." + s.HELP)
			sys.exit(1)

	if speed_multiplier_offset:
		try:
			speed_multiplier_offset = int(speed_multiplier_offset)
		except ValueError as e:
			print("Improper speed multiplier offset provided." + s.HELP)
			sys.exit(1)
		else:
			if speed_multiplier >= 1:
				print("Speed multiplier offsets may only be used with slowdown speed multipliers." + s.HELP)
				sys.exit(1)
			elif speed_multiplier_offset > speed_multiplier.denominator - 1:
				print("Speed multiplier offset may not be greater than x - 1 for a slowdown of 1/x." + s.HELP)
				sys.exit(1)

	logging.debug('speed_multiplier: {}'.format(speed_multiplier))

	return speed_multiplier, speed_multiplier_offset

### FILESYSTEM ###

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
	return s.OUTPUT_PATH_BASE + music_video_name + s.OUTPUT_EXTENSION

def get_spec_path(music_video_name):
	return s.OUTPUT_PATH_BASE + music_video_name + '_spec' + s.SPEC_EXTENSION

def get_segments_dir(music_video_name):
	return s.SEGMENTS_PATH_BASE + music_video_name + '/'

def reserve_file(file_name):
	open(file_name, 'a').close()

def sanitize_filename(filename):
	keepcharacters = (' ','.','_','-','(',')','[',']')
	return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip() if filename else None

def listdir_nohidden(path):
    for file in os.listdir(path):
        if not file.startswith('.'):
            yield path + file