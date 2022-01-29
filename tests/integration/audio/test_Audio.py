import pytest

from mugen import Audio

from tests import DATA_PATH


def get_two_beats_audio() -> Audio:
    return Audio(file=f'{DATA_PATH}/audio/two_beats.mp3')


def test_audio__detects_correct_number_of_beats():
    assert len(get_two_beats_audio().beats()) == 2
