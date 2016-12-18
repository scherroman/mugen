import sys
import json
import random
import logging
import tesserocr
from PIL import Image
from moviepy.editor import *
from moviepy.video.tools.cuts import detect_scenes
from tqdm import tqdm
from collections import OrderedDict

# Project modules
import utility as util
import settings as s

def create_music_video(video_segments, audio_file):
    """
    Compile music video from video segments and audio
    """
    print("Generating music video from video segments and audio...")

    # Make sure output directory exists
    util.ensure_dir(s.OUTPUT_PATH_BASE)
    
    # Get output path for file
    output_path = util.get_output_path(s.music_video_name)

    audio = AudioFileClip(audio_file)
    music_video = concatenate_videoclips(video_segments, method="compose")
    music_video = music_video.set_audio(audio)
    music_video.write_videofile(output_path, fps=s.MOVIEPY_FPS, codec=s.MOVIEPY_CODEC, 
                                audio_bitrate=s.MOVIEPY_AUDIO_BITRATE, ffmpeg_params=['-crf', s.MOVIEPY_CRF])

def generate_video_segments(video_files, beat_interval_groups):
    """
    Generates a set of random video segments from the video files
    with durations corresponding to the durations of the beat intervals
    """
    # Get video file clips
    videos = get_video_file_clips(video_files)

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

    if s.music_video_dimensions:
        video_segments = resize_video_segments(video_segments)
    
    return video_segments, rejected_segments

def regenerate_video_segments(spec, replace_segments):
    """
    Regenerates the video segments from the videos specified in the spec
    """
    video_files = [video_file['file_path'] for video_file in spec['video_files']]
    videos = get_video_file_clips(video_files)

    print("Regenerating video segments from {} videos according to spec...".format(len(videos)))

    # Regenerate video segments from videos
    regen_video_segments = []
    for index, video_segment in enumerate(tqdm(spec['video_segments'])):
        replace_segment = True if replace_segments and index in replace_segments else False
        regen_video_segment = regenerate_video_segment(videos, video_segment, spec['video_files'], replace_segment)

        # Add metadata for music video spec
        regen_video_segment.sequence_number = index
        regen_video_segment.beat_interval_numbers = video_segment['beat_interval_numbers']
        
        regen_video_segments.append(regen_video_segment)

    if s.music_video_dimensions:
        regen_video_segments = resize_video_segments(regen_video_segments)
    
    return regen_video_segments

def save_video_segments(video_segments):
    """
    Save the individual segments that compose the music video
    """
    print("Saving video segments...")

    # Create music video's segments directory (overwrite if exists)
    segments_dir = util.get_segments_dir(s.music_video_name)
    util.recreate_dir(segments_dir)

    count = 0
    for video_segment in video_segments:
        segment_path = segments_dir + "%s" % count + s.OUTPUT_EXTENSION
        video_segment.write_videofile(segment_path, fps=s.MOVIEPY_FPS, codec=s.MOVIEPY_CODEC, 
                                      ffmpeg_params=['-crf', s.MOVIEPY_CRF])
        count += 1

def save_rejected_segments(rejected_segments):
    """
    Save the video segments that were rejected
    """
    print("Saving rejected segments...")

    # Create rejected segments directories (overwrite if exists)
    util.recreate_dir(*[s.RS_PATH_BASE, s.RS_PATH_SCENE_CHANGE, s.RS_PATH_TEXT_DETECTED, 
                        s.RS_PATH_SOLID_COLOR])

    rs_scene_change_count = 0
    rs_text_detected_count = 0
    rs_solid_color_count = 0
    for rejected_segment in rejected_segments:
        reject_type = rejected_segment['reject_type']
        video_segment = rejected_segment['video_segment']

        if reject_type == s.RS_TYPE_SCENE_CHANGE:
            segment_path = s.RS_PATH_SCENE_CHANGE + "%s" % rs_scene_change_count + s.OUTPUT_EXTENSION
            video_segment.write_videofile(segment_path, fps=s.MOVIEPY_FPS, codec=s.MOVIEPY_CODEC, 
                                          ffmpeg_params=['-crf', s.MOVIEPY_CRF])
            rs_scene_change_count += 1
        elif reject_type == s.RS_TYPE_TEXT_DETECTED:
            segment_path =  s.RS_PATH_TEXT_DETECTED + "%s" % rs_text_detected_count + s.OUTPUT_EXTENSION
            video_segment.write_videofile(segment_path, fps=s.MOVIEPY_FPS, codec=s.MOVIEPY_CODEC, 
                                          ffmpeg_params=['-crf', s.MOVIEPY_CRF])
            rs_text_detected_count += 1
        else:
            segment_path = s.RS_PATH_SOLID_COLOR + "%s" % rs_solid_color_count + s.OUTPUT_EXTENSION
            video_segment.write_videofile(segment_path, fps=s.MOVIEPY_FPS, codec=s.MOVIEPY_CODEC, 
                                          ffmpeg_params=['-crf', s.MOVIEPY_CRF])
            rs_solid_color_count += 1

def print_rejected_segment_stats(rejected_segments):
    print("# rejected segments with scene changes: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == s.RS_TYPE_SCENE_CHANGE])))
    print("# rejected segments with text detected: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == s.RS_TYPE_TEXT_DETECTED])))
    print("# rejected segments with solid colors: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == s.RS_TYPE_SOLID_COLOR])))

def save_music_video_spec(audio_file, video_files, speed_multiplier, 
                          speed_multiplier_offset, beat_stats, beat_interval_groups, 
                          video_segments):
    """
    Save reusable spec for the music video
    """
    print("Saving music video spec...")

    # Video duration is sum of video segment durations
    video_duration = sum(video_segment.duration for video_segment in video_segments) 

    spec = OrderedDict([('version', s.VERSION),
                        ('video_duration', video_duration),
                        ('speed_multiplier', float(speed_multiplier)),
                        ('speed_multiplier_offset', speed_multiplier_offset),
                        ('beats_per_minute', beat_stats['bpm']),
                        ('audio_file', {}), 
                        ('video_files', []),
                        ('video_segments', []),
                        ('beat_locations', beat_stats['beat_locations'].tolist()),
                        ('beat_intervals', beat_stats['beat_intervals'].tolist()),
                        ('bpm_estimates', beat_stats['bpm_estimates'].tolist()),
                        ('beat_interval_groups', beat_interval_groups)])

    # Add extra metadata
    audio_file_spec = OrderedDict([('file_path', audio_file),
                                   ('offset', None)])
    spec['audio_file'] = audio_file_spec

    for index, video_file in enumerate(video_files):
        video_file_spec = OrderedDict([('video_number', index),
                                       ('file_path', video_file),
                                       ('offset', None)])
        spec['video_files'].append(video_file_spec)

    for video_segment in video_segments:
        segment_spec = OrderedDict([('sequence_number', video_segment.sequence_number),
                                    ('video_number', video_files.index(video_segment.src_video_file)),
                                    ('video_start_time', video_segment.src_start_time),
                                    ('video_end_time', video_segment.src_end_time),
                                    ('duration', video_segment.duration),
                                    ('beat_interval_numbers', video_segment.beat_interval_numbers)])
        spec['video_segments'].append(segment_spec)

    spec_path = util.get_spec_path(s.music_video_name)
    with open(spec_path, 'w') as outfile:
        json.dump(spec, outfile, indent=2, ensure_ascii=False)

def save_regenerated_music_video_spec(spec, regen_video_segments):
    print("Saving regenerated music video spec...")

    spec['video_segments'] = []
    for video_segment in regen_video_segments:
        segment_spec = OrderedDict([('sequence_number', video_segment.sequence_number),
                                    ('video_number', next(video_file['video_number'] for video_file in spec['video_files'] if video_file['file_path']==video_segment.src_video_file)),
                                    ('video_start_time', video_segment.src_start_time),
                                    ('video_end_time', video_segment.src_end_time),
                                    ('duration', video_segment.duration),
                                    ('beat_interval_numbers', video_segment.beat_interval_numbers)])
        spec['video_segments'].append(segment_spec)

    spec_path = util.get_spec_path(s.music_video_name)
    with open(spec_path, 'w') as outfile:
        json.dump(spec, outfile, indent=2, ensure_ascii=False)

### HELPER FUNCTIONS ###

def get_video_file_clips(video_files):
    """
    Returns a list of videoFileClips from a list of video file names,
    excluding those that could not be properly read
    """
    # Remove improper video files
    video_file_clips = []
    for video_file in video_files:
        try:
            video_file_clip = VideoFileClip(video_file).without_audio()
        except Exception as e:
            print("Error reading video file '{}'. Will be excluded from the music video. Error: {}".format(video_file, e))
            continue
        else:
            video_file_clip.src_file = video_file
            video_file_clips.append(video_file_clip)

    # If no video files to work with, exit
    if len(video_file_clips) == 0:
        print("No more video files left to work with. I can't continue :(")
        sys.exit(1)

    return video_file_clips

def generate_video_segment(videos, duration):
    """
    Generates a random video segment with the specified duration from the given videos 
    """
    video_segment = None
    rejected_segments = []
    while video_segment == None:
        random_video_number = random.randint(0, len(videos) - 1)
        random_video = videos[random_video_number]
        start_time = round(random.uniform(0, random_video.duration - duration), s.DURATION_PRECISION)
        end_time = start_time + round(duration, s.DURATION_PRECISION)

        video_segment = random_video.subclip(start_time,end_time)
        # Add metadata for music video spec
        video_segment.src_video_file = random_video.src_file
        video_segment.src_start_time = start_time
        video_segment.src_end_time = end_time

        # Discard video segment if there is a scene change
        reject_type = None
        if segment_contains_scene_change(video_segment):
            reject_type = s.RS_TYPE_SCENE_CHANGE
        # Discard video segment if there is any detectable text
        elif segment_contains_text(video_segment):
            reject_type = s.RS_TYPE_TEXT_DETECTED
        # Discard video segment if it contains a solid color
        elif segment_has_solid_color(video_segment):
            reject_type = s.RS_TYPE_SOLID_COLOR

        if reject_type:
            rejected_segments.append({'reject_type':reject_type, 'video_segment': video_segment})
            video_segment = None

    return video_segment, rejected_segments

def regenerate_video_segment(videos, video_segment, video_files, replace_segment):
    """
    Attempts to regenerate a spec file video segment
    If it cannot do so successfully, generates a random video segment 'B' from the given videos 
    with the same duration
    """
    regen_video_segment = None

    video_file = video_files[video_segment['video_number']]
    video = next(video for video in videos if video.src_file==video_file['file_path'])
    start_time = video_segment['video_start_time']
    end_time = video_segment['video_end_time']
    offset = video_file['offset'] if video_file['offset'] else 0

    if replace_segment:
        regen_video_segment, rejected_segments = generate_video_segment(videos, video_segment['duration'])
    else:
        try:
            regen_video_segment = video.subclip(start_time + offset,end_time + offset)
            # Add metadata for music video spec
            regen_video_segment.src_video_file = video_file['file_path']
            regen_video_segment.src_start_time = start_time
            regen_video_segment.src_end_time = end_time
        except Exception as e:
            # If we run into an error regenerating a video segment, 
            # replace it a random video segment
            print("Error regenerating video segment {}, Will generate a random video segment to replace it instead. Error: {}".format(video_segment['sequence_number'], e))
            regen_video_segment, rejected_segments = generate_video_segment(videos, video_segment['duration'])

    return regen_video_segment

def resize_video_segments(video_segments):
    resized_video_segments = []

    music_video_aspect_ratio = s.music_video_dimensions[0]/float(s.music_video_dimensions[1])

    for video_segment in video_segments:
        resized_video_segment = None
        width = video_segment.size[0]
        height = video_segment.size[1]
        aspect_ratio = width/float(height)

        # Crop video segment if needed, to match aspect ratio of music video dimensions
        if aspect_ratio > music_video_aspect_ratio:
            # Crop sides
            cropped_width = int(music_video_aspect_ratio * height)
            width_difference = width - cropped_width
            video_segment = video_segment.crop(x1 = width_difference/2, x2 = width - width_difference/2)
        elif aspect_ratio < music_video_aspect_ratio:
            # Crop top & bottom
            cropped_height = int(width/music_video_aspect_ratio)
            height_difference = height - cropped_height
            cropped_dimensions = (width, cropped_height)
            video_segment = video_segment.crop(y1 = height_difference/2, y2 = height - height_difference/2)

        # Resize video if needed, to match music video dimensions
        if tuple(video_segment.size) != s.music_video_dimensions:
            # Video needs resize
            resized_video_segment = video_segment.resize(s.music_video_dimensions)
        else:
            # Video is already correct size
            resized_video_segment = video_segment
            
        resized_video_segments.append(resized_video_segment)

    return resized_video_segments

def segment_contains_scene_change(video_segment):
    """
    Checks if a video segment contains a scene change
    """
    cuts, luminosities = detect_scenes(video_segment, fps=s.MOVIEPY_FPS, progress_bar=False)

    return True if len(cuts) > 1 else False
        
def segment_contains_text(video_segment):
    """
    Checks if a video segment contains text
    """
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
    """
    Checks if a video segment contains a solid color or close to a solid color
    """
    first_frame_is_solid_color = False
    last_frame_is_solid_color = False
    first_frame = video_segment.get_frame(t='00:00:00')
    last_frame = video_segment.get_frame(t=video_segment.duration)

    #Check first frame
    frame_image = Image.fromarray(first_frame)
    extrema = frame_image.convert("L").getextrema()
    if abs(extrema[1] - extrema[0]) <= s.MIN_EXTREMA_RANGE:
        first_frame_is_solid_color = True

    #Check last frame
    frame_image = Image.fromarray(last_frame)
    extrema = frame_image.convert("L").getextrema()
    if abs(extrema[1] - extrema[0]) <= s.MIN_EXTREMA_RANGE:
        last_frame_is_solid_color = True

    return True if first_frame_is_solid_color or last_frame_is_solid_color else False

def get_music_video_dimensions(video_files):
    """
    Returns the largest widescreen (16:9) dimensions possible for a group of videos
    """
    # Get video file clips
    music_video_dimensions = None
    largest_widescreen_dimensions = None
    videos = get_video_file_clips(video_files)
    logging.debug("\n")

    unique_dimensions = set()

    for video in videos:
        closest_widescreen_dimensions = None
        width = video.size[0]
        height = video.size[1]
        aspect_ratio = width/float(height)
        unique_dimensions.add((width, height))
        
        logging.debug(video.src_file)
        logging.debug("dimensions: {}".format(video.size))

        # Crop sides
        if aspect_ratio > s.WIDESCREEN_ASPECT_RATIO:
            cropped_width = int(s.WIDESCREEN_ASPECT_RATIO * height)
            closest_widescreen_dimensions = (cropped_width, height)
        # Crop top & bottom
        elif aspect_ratio < s.WIDESCREEN_ASPECT_RATIO:
            cropped_height = int(width/s.WIDESCREEN_ASPECT_RATIO)
            closest_widescreen_dimensions = (width, cropped_height)
        else:
            closest_widescreen_dimensions = (width, height)

        logging.debug("closest_widescreen_dimensions: {}\n".format(closest_widescreen_dimensions))

        # Check if the closest_widescreen_dimensions are the largest so far
        if not largest_widescreen_dimensions:
            largest_widescreen_dimensions = closest_widescreen_dimensions
        elif closest_widescreen_dimensions[0] * closest_widescreen_dimensions[1] > \
             largest_widescreen_dimensions[0] * largest_widescreen_dimensions[1]:
            largest_widescreen_dimensions = closest_widescreen_dimensions

    # Only one set of dimensions, use those
    if len(unique_dimensions) == 1:
        music_video_dimensions = next(iter(unique_dimensions))
        print("Using video dimensions: {}".format(music_video_dimensions))
    # Multiple sets of dimensions, use the largest widescreen dimensions calculated
    else:
        music_video_dimensions = largest_widescreen_dimensions
        print("Multiple video sizes detected. Using largest widescreen dimensions possible: {}".format(music_video_dimensions))
        
    return music_video_dimensions




