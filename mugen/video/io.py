import json
import pysrt
from collections import OrderedDict

# Project modules
import mugen.audio.audio as audio
import mugen.utility as util
import mugen.exceptions as ex
import mugen.settings as s

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
                                      ffmpeg_params=['-crf', s.music_video_crf])
        count += 1

def save_rejected_segments(rejected_segments):
    """
    Save the video segments that were rejected
    """
    print("Saving rejected segments...")

    # Create rejected segments directories (overwrite if exists)
    util.recreate_dir(*[s.RS_PATH_BASE, s.RS_PATH_REPEAT, s.RS_PATH_SCENE_CHANGE, s.RS_PATH_TEXT_DETECTED, 
                        s.RS_PATH_SOLID_COLOR])

    rs_repeat_count = 0
    rs_scene_change_count = 0
    rs_text_detected_count = 0
    rs_solid_color_count = 0
    for rejected_segment in rejected_segments:
        reject_type = rejected_segment['reject_type']
        video_segment = rejected_segment['video_segment']

        if reject_type == s.RS_TYPE_REPEAT:
            segment_path = s.RS_PATH_REPEAT + "%s" % rs_repeat_count + s.OUTPUT_EXTENSION
            video_segment.write_videofile(segment_path, fps=s.MOVIEPY_FPS, codec=s.MOVIEPY_CODEC, 
                                          ffmpeg_params=['-crf', s.music_video_crf])
            rs_repeat_count += 1
        elif reject_type == s.RS_TYPE_SCENE_CHANGE:
            segment_path = s.RS_PATH_SCENE_CHANGE + "%s" % rs_scene_change_count + s.OUTPUT_EXTENSION
            video_segment.write_videofile(segment_path, fps=s.MOVIEPY_FPS, codec=s.MOVIEPY_CODEC, 
                                          ffmpeg_params=['-crf', s.music_video_crf])
            rs_scene_change_count += 1
        elif reject_type == s.RS_TYPE_TEXT_DETECTED:
            segment_path =  s.RS_PATH_TEXT_DETECTED + "%s" % rs_text_detected_count + s.OUTPUT_EXTENSION
            video_segment.write_videofile(segment_path, fps=s.MOVIEPY_FPS, codec=s.MOVIEPY_CODEC, 
                                          ffmpeg_params=['-crf', s.music_video_crf])
            rs_text_detected_count += 1
        else:
            segment_path = s.RS_PATH_SOLID_COLOR + "%s" % rs_solid_color_count + s.OUTPUT_EXTENSION
            video_segment.write_videofile(segment_path, fps=s.MOVIEPY_FPS, codec=s.MOVIEPY_CODEC, 
                                          ffmpeg_params=['-crf', s.music_video_crf])
            rs_solid_color_count += 1

### SPEC FILES ###

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
        video_segment.video_number = video_files.index(video_segment.src_video_file)
        segment_spec = get_segment_spec(video_segment)
        spec['video_segments'].append(segment_spec)

    spec_path = util.get_spec_path(s.music_video_name)
    with open(spec_path, 'w') as outfile:
        json.dump(spec, outfile, indent=2, ensure_ascii=False)

    return spec

def save_regenerated_music_video_spec(spec, regen_video_segments):
    """
    Save reusable spec for the regenerated music video
    """
    print("Saving regenerated music video spec...")

    spec['video_segments'] = []
    for video_segment in regen_video_segments:
        video_segment.video_number = next(video_file['video_number'] for video_file in spec['video_files'] if video_file['file_path']==video_segment.src_video_file)
        segment_spec = get_segment_spec(video_segment)
        spec['video_segments'].append(segment_spec)

    spec_path = util.get_spec_path(s.music_video_name)
    with open(spec_path, 'w') as outfile:
        json.dump(spec, outfile, indent=2, ensure_ascii=False)

    return spec

def get_segment_spec(video_segment):
    return OrderedDict([('sequence_number', video_segment.sequence_number),
                        ('video_number', video_segment.video_number),
                        ('video_start_time', video_segment.src_start_time),
                        ('video_end_time', video_segment.src_end_time),
                        ('duration', video_segment.duration),
                        ('beat_interval_numbers', video_segment.beat_interval_numbers)])

### SUBTITLES ###

def add_auxiliary_tracks(video_file, spec):
    """
    Add metadata subtitle tracks to music video
    """
    print("Writing final video {} with auxiliary tracks...".format(util.get_output_path(s.music_video_name)))
    
    output_path = util.get_output_path(s.music_video_name)

    # Audio Tracks
    audio_track_beat_locations = audio.get_marked_audio_file(spec['audio_file']['file_path'], spec['beat_locations'])

    # Subtitle Tracks
    subtitle_track_segment_numbers = create_subtitle_track(spec, s.SUBS_TRACK_SEGMENT_NUMBERS)
    subtitle_track_segment_durations = create_subtitle_track(spec, s.SUBS_TRACK_SEGMENT_DURATIONS)

    # Create new music video with auxiliary audio & subtitle tracks mixed in
    ffmpeg_cmd = [
            util.get_ffmpeg_binary(),
            '-y',
            '-i', video_file,
            '-i', audio_track_beat_locations,
            '-i', subtitle_track_segment_numbers,
            '-i', subtitle_track_segment_durations,
            '-map', '0',
            '-c', 'copy',
            '-map', '1',
            '-c', 'copy', '-metadata:s:a:1', 'title={}'.format(s.AUDIO_TRACK_BEAT_LOCATIONS),
            '-map', '2',
            '-c:s:0', 'srt', '-metadata:s:s:0', 'title={}'.format(s.SUBS_TRACK_SEGMENT_NUMBERS),
            '-map', '3',
            '-c:s:1', 'srt', '-metadata:s:s:1', 'title={}'.format(s.SUBS_TRACK_SEGMENT_DURATIONS),
            output_path
          ]

    try:
        util.execute_ffmpeg_command(ffmpeg_cmd)
    except ex.FFMPEGError as e:
        print("Failed to add subtitles to music video. ffmpeg returned error code: {}\n\nOutput from ffmpeg:\n\n{}".format(e.return_code, e.stderr))

def create_subtitle_track(spec, track_type):
    subtitle_path = util.get_temp_subtitle_path(s.music_video_name, track_type)

    util.touch(subtitle_path)
    subs = pysrt.open(subtitle_path, encoding='utf-8')

    running_time = 0
    for index, video_segment in enumerate(spec['video_segments']):
        start_time = pysrt.SubRipTime.from_ordinal(running_time * 1000)
        end_time = start_time + pysrt.SubRipTime.from_ordinal(video_segment['duration'] * 1000)
        next_sub = pysrt.SubRipItem(index=index, start=start_time, end=end_time)

        if track_type == s.SUBS_TRACK_SEGMENT_NUMBERS:
            next_sub.text = video_segment['sequence_number']
        elif track_type == s.SUBS_TRACK_SEGMENT_DURATIONS:
            next_sub.text = video_segment['duration']

        running_time += video_segment['duration']
        subs.append(next_sub)
    subs.save(subtitle_path, encoding='utf-8')
            
    return subtitle_path
