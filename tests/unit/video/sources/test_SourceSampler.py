import pytest

from mugen.video.sources.Source import SourceList
from mugen.video.sources.SourceSampler import SourceSampler
from tests.unit.video.sources.test_ColorSource import (
    get_black_source,
    get_orange_source,
    get_purple_source,
    get_white_source,
)


def source_sampler(weights) -> SourceSampler:
    return SourceSampler(
        SourceList(
            [
                get_black_source(),
                get_white_source(),
                get_orange_source(),
                get_purple_source(),
            ],
            weights=weights,
        )
    )


@pytest.mark.parametrize(
    "sampler, expected_segment_color", [(source_sampler([0, 0, 0, 1]), "#800080")]
)
def test_sample(sampler, expected_segment_color):
    assert sampler.sample(1).color == expected_segment_color
