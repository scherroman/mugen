import random
import moviepy.editor as moviepy
from tqdm import tqdm

# Project modules
from mugen.video import detect as v_detect, sizing as v_sizing, io as v_io, utility as v_util
import mugen.utility as util
import mugen.settings as s

def create_music_video(video_segments, audio_file, spec):
    """
    Compile music video from video segments and audio
    """
    print("Generating music video from video segments and audio...")
    
    # Get output path for file
    temp_output_path = util.get_temp_output_path(s.music_video_name)

    audio = moviepy.AudioFileClip(audio_file)
    music_video = moviepy.concatenate_videoclips(video_segments, method="compose")
    music_video = music_video.set_audio(audio)
    music_video.write_videofile(temp_output_path, fps=s.MOVIEPY_FPS, codec=s.MOVIEPY_CODEC, 
                                audio_bitrate=s.MOVIEPY_AUDIO_BITRATE, ffmpeg_params=['-crf', s.music_video_crf],
                                temp_audiofile=s.TEMP_MOVIEPY_AUDIOFILE)
    v_io.add_auxiliary_tracks(temp_output_path, spec)

def generate_video_segments(video_files, beat_interval_groups):
    """
    Generates a set of random video segments from the video files
    with durations corresponding to the durations of the beat intervals
    """
    # Get video file clips
    videos = v_util.get_video_file_clips(video_files)
    video_segments = []
    rejected_segments = [] 

    print("Grabbing random video segments from {} videos according to beat patterns...".format(len(videos)))

    # Extract video segments from videos
    for beat_interval_group in tqdm(beat_interval_groups):
        for interval in beat_interval_group['intervals']:
            video_segment, new_rejected_segments = generate_video_segment(videos, interval, video_segments)

            # Add metadata for music video spec
            video_segment.sequence_number = len(video_segments)
            video_segment.beat_interval_numbers = beat_interval_group['beat_interval_numbers']
            
            video_segments.append(video_segment)
            rejected_segments.extend(new_rejected_segments)

    if s.music_video_dimensions:
        video_segments = v_sizing.resize_video_segments(video_segments)
    
    return video_segments, rejected_segments

def regenerate_video_segments(spec, replace_segments):
    """
    Regenerates the video segments from the videos specified in the spec
    """
    video_files = [video_file['file_path'] for video_file in spec['video_files']]
    videos = v_util.get_video_file_clips(video_files)
    regen_video_segments = []

    print("Regenerating video segments from {} videos according to spec...".format(len(videos)))

    # Regenerate video segments from videos
    for index, video_segment in enumerate(tqdm(spec['video_segments'])):
        replace_segment = True if index in replace_segments else False
        if replace_segment:
            # Wait to replace segments until later
            continue

        # Regenerate segment from the spec
        regen_video_segment = regenerate_video_segment(videos, video_segment, spec['video_files'])

        if not regen_video_segment:
            # Unable to regnereate segment, add it to list of segments to replace
            replace_segments.append(index)
            continue

        # Add metadata for music video spec
        regen_video_segment.sequence_number = index
        regen_video_segment.beat_interval_numbers = video_segment['beat_interval_numbers']
        
        regen_video_segments.append(regen_video_segment)

    # Replace segments as needed and requested
    # Sort segment indeces beforehand to replace in order
    replace_segments.sort()
    for index in replace_segments:
        video_segment = spec['video_segments'][index]
        # Generate new random segment
        replacement_video_segment, rejected_segments = generate_video_segment(videos, video_segment['duration'], regen_video_segments)

        # Add metadata for music video spec
        replacement_video_segment.sequence_number = index
        replacement_video_segment.beat_interval_numbers = video_segment['beat_interval_numbers']

        regen_video_segments.insert(index, replacement_video_segment)

    if s.music_video_dimensions:
        regen_video_segments = v_sizing.resize_video_segments(regen_video_segments)
    
    return regen_video_segments

### HELPER FUNCTIONS ###

def generate_video_segment(videos, duration, video_segments_used):
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
        if not s.allow_repeats and v_detect.segment_is_repeat(video_segment, video_segments_used)[0]:
            reject_type = s.RS_TYPE_REPEAT
        elif v_detect.segment_contains_scene_change(video_segment):
            reject_type = s.RS_TYPE_SCENE_CHANGE
        # Discard video segment if there is any detectable text
        elif v_detect.segment_contains_text(video_segment):
            reject_type = s.RS_TYPE_TEXT_DETECTED
        # Discard video segment if it contains a solid color
        elif v_detect.segment_contains_solid_color(video_segment):
            reject_type = s.RS_TYPE_SOLID_COLOR

        if reject_type:
            rejected_segments.append({'reject_type':reject_type, 'video_segment': video_segment})
            video_segment = None

    return video_segment, rejected_segments

def regenerate_video_segment(videos, video_segment, video_files):
    """
    Attempts to regenerate a spec file video segment.
    If this cannot be done successfully, returns null
    """
    regen_video_segment = None

    video_file = video_files[video_segment['video_number']]
    video = next(video for video in videos if video.src_file==video_file['file_path'])
    start_time = video_segment['video_start_time']
    end_time = video_segment['video_end_time']
    offset = video_file['offset'] if video_file['offset'] else 0

    try:
        regen_video_segment = video.subclip(start_time + offset,end_time + offset)
        # Add metadata for music video spec
        regen_video_segment.src_video_file = video_file['file_path']
        regen_video_segment.src_start_time = start_time
        regen_video_segment.src_end_time = end_time
    except Exception as e:
        regen_video_segment = None

    return regen_video_segment
