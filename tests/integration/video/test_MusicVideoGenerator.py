from mugen import MusicVideoGenerator, MusicVideo

from tests import DATA_PATH

from tests.integration.video.sources.test_VideoSource import shinsekai_source


def test_music_video_generator__creates_music_video(shinsekai_source):
    generator = MusicVideoGenerator(audio_file=f'{DATA_PATH}/audio/soft.mp3', video_sources=[shinsekai_source])
    music_video = generator.generate_from_events(generator.audio.beats(), progress_bar=False)


def test_music_video_generator__creates_preview():
    generator = MusicVideoGenerator(audio_file=f'{DATA_PATH}/audio/soft.mp3')
    preview_path = generator.preview_events(generator.audio.beats(), progress_bar=False)
