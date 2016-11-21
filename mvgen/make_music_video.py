import os
import sys
import random
import argparse
import essentia
import essentia.standard
from moviepy.editor import *
from tqdm import tqdm
import Tkinter as tk
import tkFileDialog

OUTPUT_PATH_BASE = "output/"
OUTPUT_NAME = "music_video"
OUTPUT_EXTENSION = '.mp4'

# Extracts beat locations and intervals from an audio file
def get_beat_stats(audio_file):
	print "Processing audio beat patterns..."

	# Load audio
	loader = None
	try:
		loader = essentia.standard.MonoLoader(filename = audio_file)
	except Exception as e:
		print(e)
		sys.exit(1)
	audio = loader()
	# print audio

	# Get beat stats from audio
	rhythm_loader = essentia.standard.RhythmExtractor2013()
	rhythm = rhythm_loader(audio)
	beat_stats = {'beat_locations':rhythm[1], 'beat_intervals':rhythm[4]}
	# print beat_stats

	return beat_stats

# Generates random locations for which to segment video files 
# with lengths corresponding to the lengths of beat intervals
def get_video_segments(video_files, beat_stats):
	# Remove improper video files from video_files
	videos = []
	for video_file in video_files:
		clip = None
		try:
			clip = VideoFileClip(video_file).without_audio()
			videos.append(clip)
		except Exception as e:
			print("Error reading video file '{}'. Will be excluded from the music video.".format(video_file))
			continue

	print "Grabbing random video segments from {} videos according to beat patterns...".format(len(videos))

	# If no video files to work with, exit
	if len(videos) == 0:
		print("No more video files left to work with. I can't continue :(")
		sys.exit(1)

	# Extract video segments from videos
	video_segments = []
	for beat_interval in tqdm(beat_stats['beat_intervals']):
		random_video_number = random.randint(0, len(videos) - 1)
		random_video = videos[random_video_number]
		start_time = round(random.uniform(0, random_video.duration - beat_interval), 8)
		end_time = start_time + round(beat_interval, 8)
		video_segments.append(random_video.subclip(start_time,end_time))

		# print "start {}".format(start_time)
		# print "end {} \n".format(end_time)
	# for video_segment in video_segments:
	# 	print video_segment.duration

	return video_segments

# Compile music video from video segments and audio
def create_music_video(video_segments, audio_src, output_name):
	print "Generating music video from video segments and audio..."

	# Get output path for file
	output_path = get_output_path(output_name)

	audio = AudioFileClip(audio_src)
	music_video = concatenate_videoclips(video_segments)
	music_video = music_video.set_audio(audio)
	music_video.write_videofile(output_path, fps=24, codec="libx264", audio_bitrate="320K")

def get_output_path(output_name):
	output_path = None

	if output_name == None:
		count = 0
		while os.path.exists(OUTPUT_PATH_BASE + OUTPUT_NAME + "_%s" % count + OUTPUT_EXTENSION):
			count += 1
		output_path = OUTPUT_PATH_BASE + OUTPUT_NAME + "_%s" % count + OUTPUT_EXTENSION
	else:
		output_path = OUTPUT_PATH_BASE + output_name + OUTPUT_EXTENSION

	return output_path

def listdir_nohidden(path):
    for file in os.listdir(path):
        if not file.startswith('.'):
            yield path + file

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--audio-source', dest='audio_src', help='The audio file for the music video. Supports any audio format supported by ffmpeg, such as wav, aiff, flac, ogg, mp3, etc...')
	parser.add_argument('-v', '--video-source', dest='video_src', help='The video(s) for the music video. Either a singular video file or a folder containing multiple video files. Supports any video format supported by ffmpeg, such as .ogv, .mp4, .mpeg, .avi, .mov, etc...')
	parser.add_argument('-o', '--output-name', dest='output_name', help='The name for the music video. Otherwise will output music_video_0' + OUTPUT_EXTENSION + ', music_video_1' + OUTPUT_EXTENSION + ', etc...')
	parser.add_argument('-im', '--input-manually', dest='input_manually', action='store_true', default=False, help='Pass in this argument to skip the file selection dialog and manually input the audio and video sources via the -a and -v arguments.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	input_manually = args.input_manually
	audio_src = args.audio_src
	video_src = args.video_src
	output_name = args.output_name if args.output_name else None

	if input_manually and (audio_src is None or video_src is None):
		print("Arguments -a/--audio-source and -v/--video-source are required when -im/--input-manually is specified.".format(audio_src))
		sys.exit(1)

	video_files = []

	# Read files from terminal input
	if input_manually: 
		audio_src_exists = os.path.exists(audio_src)
		video_src_exists = os.path.exists(video_src)
		video_src_is_dir = os.path.isdir(video_src)

		# Check that audio file exists
		if not audio_src_exists:
			print("Audio source path '{}' does not exist.".format(audio_src))
			sys.exit(1)

		# Check that video file/directory exists
		if not video_src_exists:
			print("Video source path {} does not exist.".format(video_src))
			sys.exit(1)

		# Check if video source is file or directory	
		if video_src_is_dir:
			video_files = [file for file in listdir_nohidden(video_src) if os.path.isfile(os.path.join(video_src, file))]
		else:
			video_files = [video_src]
	# Read files from file selection dialog
	else:
		root = tk.Tk()
		root.withdraw()
		audio_src = tkFileDialog.askopenfilename(message="Select audio file")
		video_src = tkFileDialog.askopenfilename(message="Select video file(s)", multiple=True)
	
		if audio_src == "":
			print("No audio file was selected.".format(audio_src))
			sys.exit(1)

		if video_src == "":
			print("No video file(s) were selected.".format(audio_src))
			sys.exit(1)

		video_files = list(video_src)

	# print "audio_src {}".format(audio_src)
	# print "video_src {}".format(video_src)
	# print "video_files: {}".format(video_files)

	# Get beat locations and intervals from audio file
	beat_stats = get_beat_stats(audio_src)

	# Generate video segments according to beat intervals in audio file
	video_segments = get_video_segments(video_files, beat_stats)

	# Compile music video from video segments and audio
	create_music_video(video_segments, audio_src, output_name)
