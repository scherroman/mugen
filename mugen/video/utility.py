import sys

# Project modules
import mugen.constants as c
import mugen.utility as util
import mugen.paths as paths
from mugen.video.VideoSegment import VideoSegment

def reserve_music_video_file(music_video_name):
    util.touch(paths.music_video_output_path(music_video_name))

def get_videos(video_files):
    """
    Returns a list of videoFileClips from a list of video file names,
    excluding those that could not be properly read
    """
    # Remove improper video files
    videos = []
    for video_file in video_files:
        try:
            video = VideoSegment(video_file)
        except Exception as e:
            print("Error reading video file '{}'. Will be excluded from the music video. Error: {}".format(video_file, e))
            continue
        else:
            videos.append(video)

    # If no video files to work with, exit
    if len(videos) == 0:
        print("No more video files left to work with. I can't continue :(")
        sys.exit(1)

    return videos

def print_rejected_segment_stats(rejected_segments):
    print("# rejected segment repeats: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == c.VideoTrait.IS_REPEAT])))
    print("# rejected segments with scene changes: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == c.VideoTrait.HAS_SCENE_CHANGE])))
    print("# rejected segments with text detected: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == c.VideoTrait.HAS_TEXT])))
    print("# rejected segments with solid colors: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == c.VideoTrait.HAS_SOLID_COLOR])))