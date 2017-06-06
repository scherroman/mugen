from typing import List, NamedTuple, Optional as Opt, Any

import pysrt

import mugen.exceptions as ex
import mugen.location_utility as loc_util
import mugen.utility as util
from mugen.utility import temp_file_enabled

SUBTITLES_EXTENSION = '.srt'


""" SUBTITLES """


class Subtitle(NamedTuple):
    """
    start_time: (sec)
    end_time: (sec)
    """
    text: str
    start_time: float
    end_time: float


class SubtitleTrack:
    name: str
    subtitles: List[Subtitle]
    default: bool

    def __init__(self, subtitles: List[Subtitle], name: str, *, default: bool = False):
        self.subtitles = subtitles
        self.name = name
        self.default = default

    @classmethod
    def create(cls, texts: List[Any], name: str, *, locations: Opt[List[float]] = None,
               durations: Opt[List[float]] = None, default: bool = False) -> 'SubtitleTrack':
        subtitles = []
        if locations:
            start_times, end_times = loc_util.start_end_locations_from_locations(locations)
        elif durations:
            start_times, end_times = loc_util.start_end_locations_from_intervals(durations)
        else:
            raise ex.ParameterError(f"Must provide either locations or durations for the subtitle track {name}")

        for index, (text, start_time, end_time) in enumerate(zip(texts, start_times, end_times)):
            subtitle = Subtitle(str(text), start_time, end_time)
            subtitles.append(subtitle)

        subtitle_track = cls(subtitles, name, default=default)

        return subtitle_track

    @temp_file_enabled('output_path', SUBTITLES_EXTENSION)
    def write_to_file(self, output_path: Opt[str] = None):
        util.touch(output_path)
        sub_rip_file = pysrt.open(output_path, encoding='utf-8')

        for index, sub in enumerate(self.subtitles):
            start_time = pysrt.SubRipTime.from_ordinal(sub.start_time * 1000)
            end_time = pysrt.SubRipTime.from_ordinal(sub.end_time * 1000)
            next_sub = pysrt.SubRipItem(index=index, text=sub.text, start=start_time, end=end_time)
            sub_rip_file.append(next_sub)

        sub_rip_file.save(output_path, encoding='utf-8')

        return output_path


class AudioTrack:
    name: str
    audio_file: List[Subtitle]

    def __init__(self, audio_file: str, name: str):
        self.audio_file = audio_file
        self.name = name


def add_tracks_to_video(video_file: str, output_path: str, *, subtitle_tracks: Opt[List[SubtitleTrack]] = None,
                        audio_tracks: Opt[List[AudioTrack]] = None):
    """
    Adds metadata subtitle tracks to a video
    """
    if subtitle_tracks is None:
        subtitle_tracks = []
    if audio_tracks is None:
        audio_tracks = []

    # Create temporary subtitle track files
    subtitle_files = []
    for track in subtitle_tracks:
        temp_subtitle_file = track.write_to_file()
        subtitle_files.append(temp_subtitle_file)

    # Create new music video with auxiliary audio & subtitle tracks mixed in
    ffmpeg_cmd = [
                       util.get_ffmpeg_binary(),
                       '-y',
                       '-i', video_file
          ]
    for track in audio_tracks:
        ffmpeg_cmd += [
                       '-i', track.audio_file
                      ]
    for file in subtitle_files:
        ffmpeg_cmd += [
                       '-i', file
                      ]
    ffmpeg_cmd += [
                       '-map', '0',
                       '-c', 'copy'
                  ]
    for index, track in enumerate(audio_tracks):
        ffmpeg_cmd += [
                       '-map', f'{index + 1}',
                       '-c', 'copy', f'-metadata:s:a:{index}', f'title={track.name}',
                      ]
    for index, track in enumerate(subtitle_tracks):
        ffmpeg_cmd += [
                       '-map', f'{index + 1 + len(audio_tracks)}',
                       f'-c:s:{index}', 'srt', f'-metadata:s:s:{index}', f'title={track.name}',
                      ]
        if track.default:
            ffmpeg_cmd += [
                       f'-disposition:s:{index}', 'default'
                          ]
    ffmpeg_cmd += [
                       output_path
                  ]

    try:
        util.execute_ffmpeg_command(ffmpeg_cmd)
    except ex.FFMPEGError as e:
        print(f"Failed to add subtitle tracks to music video. Error Code: {e.return_code}, "
              f"Error: {e}")
        raise
