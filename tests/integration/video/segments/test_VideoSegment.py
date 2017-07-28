import pytest

from mugen.video.segments.VideoSegment import VideoSegment

from tests import DATA_PATH


@pytest.fixture
def shinsekai_segment() -> VideoSegment:
    return VideoSegment(f'{DATA_PATH}/video/shinsekai.mp4')
