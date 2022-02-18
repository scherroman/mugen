import pytest

from mugen import lists
from mugen.lists import MugenList


class Dummy(object):
    foo = 1


def get_mugen_list():
    return MugenList([Dummy(), Dummy(), Dummy(), Dummy(), Dummy(), Dummy()])


@pytest.mark.parametrize("list, expected_foo", [(get_mugen_list(), [1, 1, 1, 1, 1, 1])])
def test_lget(list, expected_foo):
    assert list.lget("foo") == expected_foo


@pytest.mark.parametrize(
    "list, expected_l", [([1, [2, 3], [[4, 5], [6, 7]]], [1, 2, 3, 4, 5, 6, 7])]
)
def test_flatten(list, expected_l):
    assert lists.flatten(list) == expected_l


def test_mugen_list__operations_yield_mugen_list():
    assert type(MugenList() + MugenList()) == MugenList
    assert type(MugenList()[1:2]) == MugenList
