import json
from collections import OrderedDict

import pysrt

import mugen.audio.audio as audio
import mugen.constants as c
import mugen.video.constants as vc
import mugen.audio.constants as ac
import mugen.exceptions as ex
import mugen.paths as paths
import mugen.utility as util


def save_rejected_segments(rejected_segments):
    """
    Save the video segments that were rejected
    """
    print("Saving rejected segments...")

    # Create rejected segments directories (overwrite if exists)
    util.recreate_dir(*[paths.SR_PATH_BASE, paths.SR_PATH_IS_REPEAT, paths.SR_PATH_HAS_SCENE_CHANGE, paths.SR_PATH_HAS_TEXT,
                        paths.SR_PATH_HAS_SOLID_COLOR])

    rs_repeat_count = 0
    rs_scene_change_count = 0
    rs_text_detected_count = 0
    rs_solid_color_count = 0
    for segment in rejected_segments:
        if segment.reject_type == c.VideoTrait.IS_REPEAT:
            segment_path = paths.SR_PATH_IS_REPEAT + "%s" % rs_repeat_count + paths.VIDEO_OUTPUT_EXTENSION
            segment.write_videofile(segment_path, codec=c.DEFAULT_VIDEO_CODEC,
                                    ffmpeg_params=['-crf', c.DEFAULT_VIDEO_CRF])
            rs_repeat_count += 1
        elif segment.reject_type == c.VideoTrait.HAS_SCENE_CHANGE:
            segment_path = paths.SR_PATH_HAS_SCENE_CHANGE + "%s" % rs_scene_change_count + paths.VIDEO_OUTPUT_EXTENSION
            segment.write_videofile(segment_path, codec=c.DEFAULT_VIDEO_CODEC,
                                    ffmpeg_params=['-crf', c.DEFAULT_VIDEO_CRF])
            rs_scene_change_count += 1
        elif segment.reject_type == c.VideoTrait.HAS_TEXT:
            segment_path = paths.SR_PATH_HAS_TEXT + "%s" % rs_text_detected_count + paths.VIDEO_OUTPUT_EXTENSION
            segment.write_videofile(segment_path, codec=c.DEFAULT_VIDEO_CODEC,
                                    ffmpeg_params=['-crf', c.DEFAULT_VIDEO_CRF])
            rs_text_detected_count += 1
        else:
            segment_path = paths.SR_PATH_HAS_SOLID_COLOR + "%s" % rs_solid_color_count + paths.VIDEO_OUTPUT_EXTENSION
            segment.write_videofile(segment_path, codec=c.DEFAULT_VIDEO_CODEC,
                                    ffmpeg_params=['-crf', c.DEFAULT_VIDEO_CRF])
            rs_solid_color_count += 1

""" SPEC FILES """

def save_music_video_spec(audio_file, video_files, speed_multiplier, 
                          speed_multiplier_offset, beat_stats, beat_interval_groups, 
                          video_segments):
    """
    Save reusable spec for the music video
    """
    print("Saving music video spec...")

    # Video duration is sum of video segment durations
    video_duration = sum(video_segment.duration for video_segment in video_segments) 

    spec = OrderedDict([('version', c.VERSION),
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
        segment_spec = video_segment.to_spec()
        spec['video_segments'].append(segment_spec)

    spec_path = paths.spec_output_path(c.music_video_name)
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
        segment_spec = video_segment.to_spec()
        spec['video_segments'].append(segment_spec)

    spec_path = paths.spec_output_path(c.music_video_name)
    with open(spec_path, 'w') as outfile:
        json.dump(spec, outfile, indent=2, ensure_ascii=False)

    return spec

""" SUBTITLES """

def add_auxiliary_tracks(video_file, spec):
    """
    Add metadata subtitle tracks to music video
    """
    print("Writing final video {} with auxiliary tracks...".format(paths.music_video_output_path(c.music_video_name)))
    
    output_path = paths.music_video_output_path(c.music_video_name)

    # Audio Tracks
    audio_track_beat_locations = audio.create_temp_marked_audio_file(spec['audio_file']['file_path'], spec['beat_locations'])

    # Subtitle Tracks
    subtitle_track_segment_numbers = create_subtitle_track(spec, vc.SubtitlesTrack.SEGMENT_NUMBERS)
    subtitle_track_segment_durations = create_subtitle_track(spec, vc.SubtitlesTrack.SEGMENT_DURATIONS)

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
            '-c', 'copy', '-metadata:s:a:1', 'title={}'.format(ac.AudioTrack.CUT_LOCATIONS),
            '-map', '2',
            '-c:s:0', 'srt', '-metadata:s:s:0', 'title={}'.format(vc.SubtitlesTrack.SEGMENT_NUMBERS),
            '-map', '3',
            '-c:s:1', 'srt', '-metadata:s:s:1', 'title={}'.format(vc.SubtitlesTrack.SEGMENT_DURATIONS),
            output_path
          ]

    try:
        util.execute_ffmpeg_command(ffmpeg_cmd)
    except ex.FFMPEGError as e:
        print(f"Failed to add subtitles to music video. Error Code: {e.return_code}, "
              f"Error: {e}")
        raise

def create_subtitle_track(spec, track_type):
    subtitle_path = paths.generate_temp_file_path(paths.SUBTITLES_EXTENSION)

    util.touch(subtitle_path)
    subs = pysrt.open(subtitle_path, encoding='utf-8')

    running_time = 0
    for index, video_segment in enumerate(spec['video_segments']):
        start_time = pysrt.SubRipTime.from_ordinal(running_time * 1000)
        end_time = start_time + pysrt.SubRipTime.from_ordinal(video_segment['duration'] * 1000)
        next_sub = pysrt.SubRipItem(index=index, start=start_time, end=end_time)

        if track_type == c.SubtitlesTrack.SEGMENT_NUMBERS:
            next_sub.text = video_segment['sequence_number']
        elif track_type == c.SubtitlesTrack.SEGMENT_DURATIONS:
            next_sub.text = video_segment['duration']

        running_time += video_segment['duration']
        subs.append(next_sub)
    subs.save(subtitle_path, encoding='utf-8')
            
    return subtitle_path
