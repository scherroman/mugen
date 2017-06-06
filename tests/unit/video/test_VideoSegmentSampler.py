# import pytest
# from unittest.mock import MagicMock
#
# from mugen.video.VideoSegment import VideoSegment
# from mugen.video.VideoSegmentSampler import VideoSegmentSampler
#
# pytestmark = pytest.mark.skip('all tests still WIP')
#
#
# @pytest.fixture
# def mock_video_segment():
#     return MagicMock(spec=VideoSegment, duration=100, weight=1)
#
#
# @pytest.fixture
# def mock_video_segment_b():
#     return MagicMock(spec=VideoSegment, duration=200, weight=1)
#
#
# @pytest.fixture
# def mock_video_segment_c():
#     return MagicMock(spec=VideoSegment, duration=200, weight=2)
#
#
# @pytest.fixture
# def video_segment_sampler(mock_video_segment, mock_video_segment_b, mock_video_segment_c):
#     return VideoSegmentSampler([mock_video_segment, mock_video_segment_b, mock_video_segment_c])
