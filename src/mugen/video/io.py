import json
from collections import OrderedDict
from enum import Enum
from typing import List, Tuple, NamedTuple, Optional as Opt, Any

import pysrt

import mugen.constants as c
import mugen.exceptions as ex
import mugen.paths as paths
import mugen.utility as util
import mugen.location_utility as loc_util
import mugen.video.constants as vc
import mugen.audio.analysis as librosa
import mugen.audio.constants as ac
from mugen.utility import temp_file_enabled
from mugen.video.MusicVideo import MusicVideo

SUBTITLES_EXTENSION = '.srt'


def save_rejected_segments(rejected_segments):
    return
    # """
    # Save the video segments that were rejected
    # """
    # # Create rejected segments directories (overwrite if exists)
    # util.recreate_dir(*[paths.SR_PATH_BASE, paths.SR_PATH_IS_REPEAT, paths.SR_PATH_HAS_SCENE_CHANGE, paths.SR_PATH_HAS_TEXT,
    #                     paths.SR_PATH_HAS_SOLID_COLOR])
    #
    # rs_repeat_count = 0
    # rs_scene_change_count = 0
    # rs_text_detected_count = 0
    # rs_solid_color_count = 0
    # for segment in rejected_segments:
    #     if segment.reject_type == c.VideoTrait.IS_REPEAT:
    #         segment_path = paths.SR_PATH_IS_REPEAT + "%s" % rs_repeat_count + paths.VIDEO_OUTPUT_EXTENSION
    #         segment.write_videofile(segment_path, codec=c.DEFAULT_VIDEO_CODEC,
    #                                 ffmpeg_params=['-crf', c.DEFAULT_VIDEO_CRF])
    #         rs_repeat_count += 1
    #     elif segment.reject_type == c.VideoTrait.HAS_SCENE_CHANGE:
    #         segment_path = paths.SR_PATH_HAS_SCENE_CHANGE + "%s" % rs_scene_change_count + paths.VIDEO_OUTPUT_EXTENSION
    #         segment.write_videofile(segment_path, codec=c.DEFAULT_VIDEO_CODEC,
    #                                 ffmpeg_params=['-crf', c.DEFAULT_VIDEO_CRF])
    #         rs_scene_change_count += 1
    #     elif segment.reject_type == c.VideoTrait.HAS_TEXT:
    #         segment_path = paths.SR_PATH_HAS_TEXT + "%s" % rs_text_detected_count + paths.VIDEO_OUTPUT_EXTENSION
    #         segment.write_videofile(segment_path, codec=c.DEFAULT_VIDEO_CODEC,
    #                                 ffmpeg_params=['-crf', c.DEFAULT_VIDEO_CRF])
    #         rs_text_detected_count += 1
    #     else:
    #         segment_path = paths.SR_PATH_HAS_SOLID_COLOR + "%s" % rs_solid_color_count + paths.VIDEO_OUTPUT_EXTENSION
    #         segment.write_videofile(segment_path, codec=c.DEFAULT_VIDEO_CODEC,
    #                                 ffmpeg_params=['-crf', c.DEFAULT_VIDEO_CRF])
    #         rs_solid_color_count += 1


""" SPEC FILES """


def save_music_video_spec(audio_file, video_files, speed_multiplier, 
                          speed_multiplier_offset, beat_stats, beat_interval_groups, 
                          video_segments):
    return
    # """
    # Save reusable spec for the music video
    # """
    # # Video duration is sum of video segment durations
    # video_duration = sum(video_segment.duration for video_segment in video_segments)
    #
    # spec = OrderedDict([('version', c.VERSION),
    #                     ('video_duration', video_duration),
    #                     ('speed_multiplier', float(speed_multiplier)),
    #                     ('speed_multiplier_offset', speed_multiplier_offset),
    #                     ('beats_per_minute', beat_stats['bpm']),
    #                     ('audio_file', {}),
    #                     ('video_files', []),
    #                     ('video_segments', []),
    #                     ('beat_locations', beat_stats['beat_locations'].tolist()),
    #                     ('beat_intervals', beat_stats['beat_intervals'].tolist()),
    #                     ('bpm_estimates', beat_stats['bpm_estimates'].tolist()),
    #                     ('beat_interval_groups', beat_interval_groups)])
    #
    # # Add extra metadata
    # audio_file_spec = OrderedDict([('file_path', audio_file),
    #                                ('offset', None)])
    # spec['audio_file'] = audio_file_spec
    #
    # for index, video_file in enumerate(video_files):
    #     video_file_spec = OrderedDict([('video_number', index),
    #                                    ('file_path', video_file),
    #                                    ('offset', None)])
    #     spec['video_files'].append(video_file_spec)
    #
    # for video_segment in video_segments:
    #     video_segment.video_number = video_files.index(video_segment.src_video_file)
    #     segment_spec = video_segment.to_spec()
    #     spec['video_segments'].append(segment_spec)
    #
    # spec_path = paths.spec_output_path(c.music_video_name)
    # with open(spec_path, 'w') as outfile:
    #     json.dump(spec, outfile, indent=2, ensure_ascii=False)
    #
    # return spec


def save_regenerated_music_video_spec(spec, regen_video_segments):
    return
    # """
    # Save reusable spec for the regenerated music video
    # """
    # print("Saving regenerated music video specmugen..")
    #
    # spec['video_segments'] = []
    # for video_segment in regen_video_segments:
    #     video_segment.video_number = next(video_file['video_number'] for video_file in spec['video_files'] if video_file['file_path']==video_segment.src_video_file)
    #     segment_spec = video_segment.to_spec()
    #     spec['video_segments'].append(segment_spec)
    #
    # spec_path = paths.spec_output_path(c.music_video_name)
    # with open(spec_path, 'w') as outfile:
    #     json.dump(spec, outfile, indent=2, ensure_ascii=False)
    #
    # return spec


""" SUBTITLES """


class Subtitle(NamedTuple):
    """
    start_time: (sec)
    end_time: (sec)
    """
    text: str
    start_time: float
    end_time: float


class TrackType(str, Enum):
    pass


class AudioTrackType(TrackType):
    CUT_LOCATIONS = 'cut_locations'
    # EVENT_LOCATIONS = 'event_locations'


class SubtitleTrackType(TrackType):
    SEGMENT_NUMBERS = 'segment_numbers'
    SEGMENT_DURATIONS = 'segment_durations'
    SPEC = 'spec'


def add_auxiliary_tracks(music_video: MusicVideo, video_file: str, output_path: str):
    """
    Add metadata subtitle tracks to a music video
    """
    # Audio Tracks
    audio_track_cut_locations = librosa.create_marked_audio_file(music_video.audio_file, music_video.cut_locations)

    # Subtitle Tracks
    durations = [segment.duration for segment in music_video.video_segments]
    indices = [index for index, _ in music_video.video_segments]

    subtitle_track_segment_numbers = create_subtitle_file(indices, durations)
    subtitle_track_segment_durations = create_subtitle_file(durations, durations)

    # Create new music video with auxiliary audio & subtitle tracks mixed in
    ffmpeg_cmd = [
            util.get_ffmpeg_binary(),
            '-y',
            '-i', video_file,
            '-i', audio_track_cut_locations,
            '-i', subtitle_track_segment_numbers,
            '-i', subtitle_track_segment_durations,
            '-map', '0',
            '-c', 'copy',
            '-map', '1',
            '-c', 'copy', '-metadata:s:a:1', 'title={}'.format(AudioTrackType.CUT_LOCATIONS),
            '-map', '2',
            '-c:s:0', 'srt', '-metadata:s:s:0', 'title={}'.format(SubtitleTrackType.SEGMENT_NUMBERS),
            '-map', '3',
            '-c:s:1', 'srt', '-metadata:s:s:1', 'title={}'.format(SubtitleTrackType.SEGMENT_DURATIONS),
            output_path
          ]

    try:
        util.execute_ffmpeg_command(ffmpeg_cmd)
    except ex.FFMPEGError as e:
        print(f"Failed to add subtitles to music video. Error Code: {e.return_code}, "
              f"Error: {e}")
        raise


@temp_file_enabled('output_path', SUBTITLES_EXTENSION)
def create_subtitle_file(texts: List[str], durations: List[float], output_path: Opt[str] = None):
    subtitles = generate_subtitles(texts, durations)
    write_subtitles_to_file(subtitles, output_path)

    return output_path


def write_subtitles_to_file(subs: List[Subtitle], output_path: str):
    util.touch(output_path)
    sub_rip_file = pysrt.open(output_path, encoding='utf-8')

    for index, sub in enumerate(subs):
        start_time = pysrt.SubRipTime.from_ordinal(sub.start_time * 1000)
        end_time = pysrt.SubRipTime.from_ordinal(sub.end_time * 1000)
        next_sub = pysrt.SubRipItem(index=index, text=sub.text, start=start_time, end=end_time)
        sub_rip_file.append(next_sub)

    sub_rip_file.save(output_path, encoding='utf-8')


def generate_subtitles(texts: List[Any], durations: List[float]) -> List[Subtitle]:
    subtitles = []
    start_times, end_times = loc_util.start_end_locations_from_intervals(durations)
    for index, (text, start_time, end_time) in enumerate(zip(texts, start_times, end_times)):
        subtitle = Subtitle(text, start_time, end_time)
        subtitles.append(subtitle)
            
    return subtitles
