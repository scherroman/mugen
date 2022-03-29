from subprocess import CalledProcessError
from typing import Any, List, NamedTuple, Optional

import pysrt

from mugen.utilities import location, system
from mugen.utilities.system import use_temporary_file_fallback

SUBTITLES_EXTENSION = ".srt"


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

    def __init__(self, name: str, subtitles: List[Subtitle]):
        self.subtitles = subtitles
        self.name = name

    @classmethod
    def create(
        cls, name: str, texts: List[Any], locations: List[float]
    ) -> "SubtitleTrack":
        subtitles = []
        start_times, end_times = location.start_end_locations_from_locations(locations)
        for text, start_time, end_time in zip(texts, start_times, end_times):
            subtitle = Subtitle(str(text), start_time, end_time)
            subtitles.append(subtitle)

        return cls(name, subtitles)

    @use_temporary_file_fallback("output_path", SUBTITLES_EXTENSION)
    def write_to_file(self, output_path: Optional[str] = None):
        system.touch(output_path)
        sub_rip_file = pysrt.open(output_path, encoding="utf-8")

        for index, sub in enumerate(self.subtitles):
            start_time = pysrt.SubRipTime.from_ordinal(sub.start_time * 1000)
            end_time = pysrt.SubRipTime.from_ordinal(sub.end_time * 1000)
            next_sub = pysrt.SubRipItem(
                index=index, text=sub.text, start=start_time, end=end_time
            )
            sub_rip_file.append(next_sub)

        sub_rip_file.save(output_path, encoding="utf-8")

        return output_path


class AudioTrack:
    name: str
    audio_file: str

    def __init__(self, audio_file: str, name: str):
        self.audio_file = audio_file
        self.name = name


def add_subtitle_tracks_to_video(
    video_file: str, subtitle_tracks: List[SubtitleTrack], output_path: str
):
    """
    Adds subtitle tracks to a video
    """
    # Create temporary subtitle track files
    subtitle_files = []
    for track in subtitle_tracks:
        subtitle_file = track.write_to_file()
        subtitle_files.append(subtitle_file)

    # Create new music video with auxiliary audio & subtitle tracks mixed in
    ffmpeg_command = ["ffmpeg", "-y", "-i", video_file]
    for file in subtitle_files:
        ffmpeg_command += ["-i", file]
    ffmpeg_command += ["-map", "0", "-c", "copy"]
    for index, track in enumerate(subtitle_tracks):
        ffmpeg_command += [
            "-map",
            f"{index + 1}",
            f"-c:s:{index}",
            "srt",
            f"-metadata:s:s:{index}",
            f"title={track.name}",
        ]
    ffmpeg_command += [output_path]

    try:
        system.run_command(ffmpeg_command)
    except CalledProcessError as error:
        print(f"Failed to add subtitle tracks to music video. \n Error: {error}")
        raise error
