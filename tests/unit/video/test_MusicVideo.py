from mugen import MusicVideo
from tests.unit.video.segments.test_ColorSegment import (
    get_black_segment,
    get_orange_segment,
    get_white_segment,
)


def get_music_video():
    return MusicVideo([get_black_segment(), get_white_segment(), get_orange_segment()])


def test_dimensions():
    assert get_music_video().dimensions == (1920, 1080)

    music_video = get_music_video()
    music_video.aspect_ratio = 4 / 3
    assert music_video.dimensions == (1440, 1080)

    music_video = get_music_video()
    music_video.dimensions = (100, 200)
    assert music_video.dimensions == (100, 200)


def test_cuts():
    music_video = get_music_video()
    assert music_video.cuts.segment_locations == [0, 1, 2]
    assert music_video.cuts.segment_durations == [1, 1, 1]


def test_compose__duration_is_sum_of_segment_durations():
    music_video = get_music_video()
    composed_music_video = music_video.compose()

    assert composed_music_video.duration == sum(
        segment.duration for segment in music_video.segments
    )
