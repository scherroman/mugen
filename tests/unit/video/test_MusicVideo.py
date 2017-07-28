import pytest

from mugen import MusicVideo

from tests.unit.video.segments.test_ColorSegment import black_segment, white_segment, orange_segment


@pytest.fixture
def music_video():
    return MusicVideo([black_segment(), white_segment(), orange_segment()])


def test_dimensions():
    assert music_video().dimensions == (1920, 1080)

    mv = music_video()
    mv.aspect_ratio = 4/3
    assert mv.dimensions == (1440, 1080)

    mv = music_video()
    mv.dimensions = (100, 200)
    assert mv.dimensions == (100, 200)


def test_cuts():
    assert music_video().cuts.segment_locations == [0, 1, 2]
    assert music_video().cuts.segment_durations == [1, 1, 1]


def test_compose__duration_is_sum_of_segment_durations():
    mv = music_video()
    composed_music_video = mv.compose()

    assert composed_music_video.duration == sum(segment.duration for segment in mv.segments)

