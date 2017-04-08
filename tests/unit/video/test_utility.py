import pytest

import mugen.video.utility as v_util


@pytest.mark.parametrize("seconds, expected", [
    (25, '00:00:25.000'),
    (500.45, '00:08:20.450'),
    (50000.085, '13:53:20.085')
])
def test_seconds_to_time_code(seconds, expected):
    assert v_util.seconds_to_time_code(seconds) == expected
