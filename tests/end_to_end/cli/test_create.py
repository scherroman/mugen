import os
import pytest
import subprocess
from subprocess import CalledProcessError

from mugen import VideoSegment, MusicVideo, Audio

from tests import DATA_PATH

def test_create__creates_music_video_successfully(tmp_path):
    audio_path = f'{DATA_PATH}/audio/two_beats.mp3'
    try:
        subprocess.run(f'mugen --output-directory {tmp_path} create --audio-source {audio_path} --video-sources {DATA_PATH}/video/tracking_shot.mp4 --video-dimensions 1500 600 --video-codec libx265'.split(), check=True, timeout=60, capture_output=True, text=True)
    except CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    music_video_path_base = f'{tmp_path}/music_video_0/music_video_0'
    music_video_path = f'{music_video_path_base}.mkv'
    music_video_save_file_path = f'{music_video_path_base}.pickle'

    # Check that output files exist
    assert os.path.isfile(music_video_path)
    assert os.path.isfile(music_video_save_file_path)

    music_video_segment = VideoSegment(music_video_path)
    loaded_music_video = MusicVideo.load(music_video_save_file_path)
    audio = Audio(audio_path)

    # Check duration
    assert len(loaded_music_video.segments) == 3
    assert music_video_segment.duration == pytest.approx(audio.duration, .1)
    assert loaded_music_video.duration == pytest.approx(audio.duration, .1)
    assert music_video_segment.duration == pytest.approx(loaded_music_video.duration, .1)

    # Check dimensions and codec
    assert music_video_segment.video_stream['width'] == 1500
    assert music_video_segment.video_stream['height'] == 600
    assert music_video_segment.video_stream['codec_name'] == 'hevc'

    # Check subtitle tracks
    assert len(music_video_segment.streams) == 5
    assert len(music_video_segment.video_streams) == 1
    assert len(music_video_segment.audio_streams) == 1
    assert len(music_video_segment.subtitle_streams) == 3
    assert music_video_segment.subtitle_streams[0]['tags']['title'] == 'segment_numbers'
    assert music_video_segment.subtitle_streams[1]['tags']['title'] == 'segment_locations_seconds'
    assert music_video_segment.subtitle_streams[2]['tags']['title'] == 'segment_durations_seconds'
    assert len(music_video_segment.get_subtitle_stream_content(0)) > 0
    assert len(music_video_segment.get_subtitle_stream_content(1)) > 0
    assert len(music_video_segment.get_subtitle_stream_content(2)) > 0


