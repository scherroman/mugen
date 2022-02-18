import os

from mugen import MusicVideo
from tests.integration.video.segments.test_ImageSegment import get_dark_image_segment
from tests.integration.video.segments.test_VideoSegment import get_tracking_shot_segment
from tests.unit.video.segments.test_ColorSegment import get_orange_segment


def get_basic_music_video() -> MusicVideo:
    short_tracking_shot_segment = get_tracking_shot_segment().subclip(end_time=1)
    return MusicVideo(
        [short_tracking_shot_segment, get_dark_image_segment(), get_orange_segment()]
    )


def test_music_video__writes_to_file():
    music_video_path = get_basic_music_video().write_to_video_file()
    assert os.path.isfile(music_video_path)


def test_music_video__saves_and_loads():
    music_video = get_basic_music_video()
    music_video_file = music_video.save()
    loaded_music_video = MusicVideo.load(music_video_file)

    assert len(loaded_music_video.segments) == len(music_video.segments)
