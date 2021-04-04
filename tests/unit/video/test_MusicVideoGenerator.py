import pytest

from mugen import MusicVideoGenerator
from mugen.exceptions import ParameterError
from tests.unit.video.sources.test_ColorSource import orange_source


def test_music_video_generator__requires_audio_file_or_duration(orange_source):
    with pytest.raises(ParameterError):
        generator = MusicVideoGenerator(video_sources=[orange_source])


def test_music_video_generator__creates_music_video_with_duration(orange_source):
    generator = MusicVideoGenerator(video_sources=[orange_source], duration=.1, video_filters=[])

    music_video = generator.generate_from_events([.02, .04], progress_bar=False)

    assert len(music_video.segments) == 3
    assert music_video.compose().duration == .1
