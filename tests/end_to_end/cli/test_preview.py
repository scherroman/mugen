import os
import subprocess
from subprocess import CalledProcessError

import pytest

from mugen import Audio, VideoSegment
from tests import TWO_BEATS_AUDIO_PATH


def test_preview__generates_audiovisual_preview_successfully(tmp_path):
    audio_path = TWO_BEATS_AUDIO_PATH
    try:
        subprocess.run(
            [
                "mugen",
                "--output-directory",
                tmp_path,
                "preview",
                "--audio-source",
                audio_path,
            ],
            check=True,
            timeout=30,
            capture_output=True,
            text=True,
        )
    except CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    preview_path = os.path.join(tmp_path, "music_video_preview_0.mkv")

    # Check that output file exists
    assert os.path.isfile(preview_path)

    preview_segment = VideoSegment(preview_path)
    audio = Audio(audio_path)

    # Check duration
    assert preview_segment.duration == pytest.approx(audio.duration, 0.1)

    # Check subtitle tracks
    assert len(preview_segment.streams) == 3
    assert len(preview_segment.video_streams) == 1
    assert len(preview_segment.audio_streams) == 1
    assert len(preview_segment.subtitle_streams) == 1
    assert preview_segment.subtitle_streams[0]["tags"]["title"] == "events"
    assert len(preview_segment.get_subtitle_stream_content(0)) > 0


def test_preview__generates_audio_preview_successfully(tmp_path):
    audio_path = TWO_BEATS_AUDIO_PATH
    try:
        subprocess.run(
            [
                "mugen",
                "--output-directory",
                tmp_path,
                "preview",
                "--audio-source",
                audio_path,
                "--preview-mode",
                "audio",
            ],
            check=True,
            timeout=30,
            capture_output=True,
            text=True,
        )
    except CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    preview_path = os.path.join(tmp_path, "music_video_preview_0.wav")

    # Check that output file exists
    assert os.path.isfile(preview_path)

    preview_audio = Audio(preview_path)
    audio = Audio(audio_path)

    # Check duration
    assert preview_audio.duration == pytest.approx(audio.duration, 0.1)
