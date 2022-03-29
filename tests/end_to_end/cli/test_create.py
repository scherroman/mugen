import os
import subprocess
from subprocess import CalledProcessError

import pytest

from mugen import Audio, MusicVideo, VideoSegment
from tests import (
    NO_BEAT_AUDIO_PATH,
    SPECIAL_CHARACTERS_VIDEO_PATH,
    TRACKING_SHOT_VIDEO_PATH,
    TWO_BEATS_AUDIO_PATH,
)


def test_create__creates_music_video_successfully(tmp_path):
    audio_path = TWO_BEATS_AUDIO_PATH
    try:
        subprocess.run(
            [
                "mugen",
                "--output-directory",
                tmp_path,
                "create",
                "--audio-source",
                audio_path,
                "--video-sources",
                TRACKING_SHOT_VIDEO_PATH,
                "--video-dimensions",
                "1500",
                "600",
                "--video-codec",
                "libx265",
            ],
            check=True,
            timeout=180,
            capture_output=True,
            text=True,
        )
    except CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    music_video_path_base = os.path.join(tmp_path, "music_video_0", "music_video_0")
    music_video_path = f"{music_video_path_base}.mkv"
    music_video_save_file_path = f"{music_video_path_base}.pickle"

    # Check that output files exist
    assert os.path.isfile(music_video_path)
    assert os.path.isfile(music_video_save_file_path)

    music_video_segment = VideoSegment(music_video_path)
    loaded_music_video = MusicVideo.load(music_video_save_file_path)
    audio = Audio(audio_path)

    # Check duration
    assert len(loaded_music_video.segments) == 3
    assert music_video_segment.duration == pytest.approx(audio.duration, 0.1)
    assert loaded_music_video.duration == pytest.approx(audio.duration, 0.1)
    assert music_video_segment.duration == pytest.approx(
        loaded_music_video.duration, 0.1
    )

    # Check dimensions and codec
    assert music_video_segment.video_stream["width"] == 1500
    assert music_video_segment.video_stream["height"] == 600
    assert music_video_segment.video_stream["codec_name"] == "hevc"

    # Check video, audio and subtitle tracks
    assert len(music_video_segment.video_streams) == 1
    assert len(music_video_segment.audio_streams) == 1
    assert len(music_video_segment.subtitle_streams) == 1
    assert len(music_video_segment.streams) == 3
    assert music_video_segment.subtitle_streams[0]["tags"]["title"] == "events"
    assert len(music_video_segment.get_subtitle_stream_content(0)) > 0


def test_create__works_with_files_with_special_characters(tmp_path):
    try:
        subprocess.run(
            [
                "mugen",
                "--output-directory",
                tmp_path,
                "create",
                "--audio-source",
                NO_BEAT_AUDIO_PATH,
                "--video-sources",
                SPECIAL_CHARACTERS_VIDEO_PATH,
                "--exclude-video-filters",
                "not_is_repeat",
            ],
            check=True,
            timeout=180,
            capture_output=True,
            text=True,
        )
    except CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    music_video_path_base = os.path.join(tmp_path, "music_video_0", "music_video_0")
    music_video_path = f"{music_video_path_base}.mkv"
    music_video_save_file_path = f"{music_video_path_base}.pickle"

    # Check that output files exist
    assert os.path.isfile(music_video_path)
    assert os.path.isfile(music_video_save_file_path)


def test_create__preserves_original_audio_when_option_is_passed(tmp_path):
    audio_path = TWO_BEATS_AUDIO_PATH
    try:
        subprocess.run(
            [
                "mugen",
                "--output-directory",
                tmp_path,
                "create",
                "--audio-source",
                audio_path,
                "--video-sources",
                TRACKING_SHOT_VIDEO_PATH,
                "--use-original-audio",
            ],
            check=True,
            timeout=180,
            capture_output=True,
            text=True,
        )
    except CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    music_video_path_base = os.path.join(tmp_path, "music_video_0", "music_video_0")
    music_video_path = f"{music_video_path_base}.mkv"
    music_video_save_file_path = f"{music_video_path_base}.pickle"

    # Check that output files exist
    assert os.path.isfile(music_video_path)
    assert os.path.isfile(music_video_save_file_path)

    music_video_segment = VideoSegment(music_video_path)
    loaded_music_video = MusicVideo.load(music_video_save_file_path)

    # Check duration
    assert len(loaded_music_video.segments) == 3
    assert music_video_segment.duration == pytest.approx(
        loaded_music_video.duration, 0.1
    )

    # Check video, audio and subtitle tracks
    assert len(music_video_segment.video_streams) == 1
    assert len(music_video_segment.audio_streams) == 1
    assert len(music_video_segment.subtitle_streams) == 1
    assert len(music_video_segment.streams) == 3
    assert music_video_segment.subtitle_streams[0]["tags"]["title"] == "events"
    assert len(music_video_segment.get_subtitle_stream_content(0)) > 0
