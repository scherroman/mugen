import pytest

from mugen.video.sources.VideoSource import VideoSource, TimeRange, VideoSourceList

from tests import DATA_PATH

SHINSEKAI_VIDEO_FILE = f'{DATA_PATH}/video/shinsekai.mp4'
SHINSEKAI_VIDEO_GLOB = f'{DATA_PATH}/video/shin*'
VIDEO_DIRECTORY = f'{DATA_PATH}/video'


@pytest.fixture
def shinsekai_source() -> VideoSource:
    return VideoSource(SHINSEKAI_VIDEO_FILE)


def five_percent_duration(video_source) -> float:
    """
    Returns a duration corresponding to five percent of the video source's duration
    """
    return video_source.segment.duration * .05


def test_sample():
    video_source = shinsekai_source()
    duration = five_percent_duration(video_source)

    assert video_source.sample(duration).duration == pytest.approx(duration)


def test_time_boundaries__single_boundary():
    video_source = shinsekai_source()
    duration = five_percent_duration(video_source)
    boundary = TimeRange(duration * 2, duration * 3.01)
    video_source.time_boundaries.append(boundary)

    assert boundary.start <= video_source.sample(duration).source_start_time <= boundary.end


def test_time_boundaries__multiple_boundaries():
    video_source = shinsekai_source()
    duration = five_percent_duration(video_source)
    boundary = TimeRange(duration * 2, duration * 3.01)
    boundary_b = TimeRange(duration * 4, duration * 5.01)
    video_source.time_boundaries.extend([boundary, boundary_b])
    sample = video_source.sample(duration)

    assert (boundary.start <= sample.source_start_time <= boundary.end or
            boundary_b.start <= sample.source_start_time <= boundary_b.end)


def test_video_source_list__populates_from_video_files():
    video_source_list = VideoSourceList([SHINSEKAI_VIDEO_FILE])

    assert type(video_source_list[0]) == VideoSource


def test_video_source_list__populates_from_directory():
    video_source_list = VideoSourceList(VIDEO_DIRECTORY)

    assert type(video_source_list[0]) == VideoSource


def test_video_source_list__populates_from_file_glob():
    video_source_list = VideoSourceList(SHINSEKAI_VIDEO_GLOB)

    assert type(video_source_list[0]) == VideoSource


def test_video_source_list__populates_from_nested_sources():
    video_source_list = VideoSourceList([SHINSEKAI_VIDEO_FILE, VIDEO_DIRECTORY,
                                         [SHINSEKAI_VIDEO_FILE, SHINSEKAI_VIDEO_GLOB]])

    assert type(video_source_list[0]) == VideoSource
