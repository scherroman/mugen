import pytest

from mugen.video.sources import SourceList
from mugen.video.sources import SourceSampler
from tests.unit.video.sources.test_ColorSource import black_source, white_source, orange_source, purple_source


@pytest.fixture
def source_sampler(weights) -> SourceSampler:
    return SourceSampler(SourceList([black_source(), white_source(), orange_source(), purple_source()],
                                    weights=weights))


@pytest.mark.parametrize("sampler, expected_segment_color", [
    (source_sampler([0, 0, 0, 1]), '#800080')
])
def test_sample(sampler, expected_segment_color):
    assert sampler.sample(1).color == expected_segment_color
