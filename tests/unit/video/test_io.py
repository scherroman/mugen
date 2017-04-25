import pytest

import mugen.video.io as v_io
from mugen.video.io import Subtitle


@pytest.mark.parametrize("texts, durations, expected_subtitles", [
    ([], [], []),
    (["hi", "yo", "ok"], [5, 10, 15], [Subtitle("hi", 0, 5), Subtitle("yo", 5, 15), Subtitle("ok", 15, 30)]),
])
def test_generate_subtitles(texts, durations, expected_subtitles):
    assert v_io.generate_subtitles(texts, durations) == expected_subtitles
