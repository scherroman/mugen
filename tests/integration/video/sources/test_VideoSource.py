import pytest

from mugen.video.sources.VideoSource import VideoSource, TimeRange, VideoSourceList
from tests import DATA_PATH

TRACKING_SHOT_VIDEO_FILE = f'{DATA_PATH}/video/tracking_shot.mp4'
TRACKING_SHOT_VIDEO_GLOB = f'{DATA_PATH}/video/tracking_shot*'
VIDEO_DIRECTORY = f'{DATA_PATH}/video'


def get_tracking_shot_source() -> VideoSource:
    return VideoSource(TRACKING_SHOT_VIDEO_FILE)


def get_five_percent_duration(video_source) -> float:
    """
    Returns a duration corresponding to five percent of the video source's duration
    """
    return video_source.segment.duration * .05


def test_sample__has_correct_duration():
    tracking_shot_source = get_tracking_shot_source()
    duration = get_five_percent_duration(tracking_shot_source)

    assert tracking_shot_source.sample(duration).duration == pytest.approx(duration)


def test_time_boundaries__single_boundary():
    tracking_shot_source = get_tracking_shot_source()
    duration = get_five_percent_duration(tracking_shot_source)
    boundary = TimeRange(duration * 2, duration * 3.01)
    tracking_shot_source.time_boundaries.append(boundary)

    assert boundary.start <= tracking_shot_source.sample(duration).source_start_time <= boundary.end


def test_time_boundaries__multiple_boundaries():
    tracking_shot_source = get_tracking_shot_source()
    duration = get_five_percent_duration(tracking_shot_source)
    boundary = TimeRange(duration * 2, duration * 3.01)
    boundary_b = TimeRange(duration * 4, duration * 5.01)
    tracking_shot_source.time_boundaries.extend([boundary, boundary_b])
    sample = tracking_shot_source.sample(duration)

    assert (boundary.start <= sample.source_start_time <= boundary.end or
            boundary_b.start <= sample.source_start_time <= boundary_b.end)


def test_video_source_list__populates_from_video_files():
    video_source_list = VideoSourceList([TRACKING_SHOT_VIDEO_FILE])

    assert type(video_source_list[0]) == VideoSource


def test_video_source_list__populates_from_directory():
    video_source_list = VideoSourceList(VIDEO_DIRECTORY)

    assert type(video_source_list[0]) == VideoSource


def test_video_source_list__populates_from_file_glob():
    video_source_list = VideoSourceList(TRACKING_SHOT_VIDEO_GLOB)

    assert type(video_source_list[0]) == VideoSource


def test_video_source_list__populates_from_nested_sources():
    video_source_list = VideoSourceList([TRACKING_SHOT_VIDEO_FILE, VIDEO_DIRECTORY,
                                         [TRACKING_SHOT_VIDEO_FILE, TRACKING_SHOT_VIDEO_GLOB]])

    assert type(video_source_list[0]) == VideoSource
