import pytest

from mugen.video.sources.VideoSource import VideoSource, TimeRange, VideoSourceList

from tests import DATA_PATH


@pytest.fixture
def shinsekai_source() -> VideoSource:
    return VideoSource(f'{DATA_PATH}/video/shinsekai.mp4')


def five_percent_duration(video_source) -> float:
    """
    Returns a duration corresponding to five percent of the video source's duration
    """
    return video_source.segment.duration * .05


def test_sample():
    video_source = shinsekai_source()
    duration = five_percent_duration(video_source)

    assert video_source.sample(duration).duration == pytest.approx(duration)


def test_time_boundaries():
    video_source = shinsekai_source()
    duration = five_percent_duration(video_source)
    boundary = TimeRange(duration * 2, duration * 3.01)
    video_source.time_boundaries.append(boundary)

    assert boundary.start <= video_source.sample(duration).source_start_time <= boundary.end


def test_video_source_list__populates_from_video_files():
    video_source_list = VideoSourceList([f'{DATA_PATH}/video/shinsekai.mp4'])

    assert type(video_source_list[0]) == VideoSource


def test_video_source_list__populates_from_directory():
    video_source_list = VideoSourceList(f'{DATA_PATH}/video')

    assert type(video_source_list[0]) == VideoSource
