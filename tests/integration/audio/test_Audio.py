import pytest

from mugen import Audio

from tests import TWO_BEATS_AUDIO_PATH


def get_two_beats_audio() -> Audio:
    return Audio(file=TWO_BEATS_AUDIO_PATH)


def test_audio__detects_correct_number_of_beats():
    assert len(get_two_beats_audio().beats()) == 2
