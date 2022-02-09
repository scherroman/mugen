import os

from mugen import MusicVideoGenerator

from tests.integration.video.sources.test_VideoSource import get_tracking_shot_source

from tests import TWO_BEATS_AUDIO_PATH


def test_music_video_generator__generates_music_video():
    generator = MusicVideoGenerator(audio_file=TWO_BEATS_AUDIO_PATH, video_sources=[get_tracking_shot_source()])
    two_beats_music_video = generator.generate_from_events(generator.audio.beats(), show_progress=False)
    music_video_path = two_beats_music_video.write_to_video_file()
    assert len(two_beats_music_video.segments) == 3
    assert os.path.isfile(music_video_path)


def test_music_video_generator__creates_preview():
    generator = MusicVideoGenerator(audio_file=TWO_BEATS_AUDIO_PATH)
    preview_path = generator.preview_events(generator.audio.beats(), show_progress=False)
    assert os.path.isfile(preview_path)
