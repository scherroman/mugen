from fractions import Fraction
from typing import List, Any

import pytest

import mugen.utility as util
from mugen.mixins.Weightable import Weightable


@pytest.fixture
def weights() -> List[float]:
    return [1, 1, 1, 1]


@pytest.fixture
def weights_b() -> List[float]:
    return [1, 1, 2, 4]


@pytest.fixture
def weights_c() -> List[float]:
    return [1/2, 1/2, 1, 1]


@pytest.fixture
def weights_d() -> List[float]:
    return [1, 3, 6, 0]


@pytest.fixture
def weightable() -> Weightable:
    return Weightable(weight=3)


@pytest.fixture
def weightables() -> List[Weightable]:
    return [Weightable(weight=1), Weightable(weight=2), Weightable(weight=4)]


@pytest.fixture
def weightables_nested() -> List[Any]:
    return [weightable(), weightables()]


@pytest.fixture
def weightables_double_nested() -> List[Any]:
    return [weightable(), [weightable(), weightables()]]


@pytest.mark.parametrize("weights, expected_weights", [
    (weights(), [1/4, 1/4, 1/4, 1/4]),
    (weights_b(), [1/8, 1/8, 2/8, 4/8]),
    (weights_c(), [.5/3, .5/3, 1/3, 1/3]),
    (weights_d(), [1/10, 3/10, 6/10, 0]),
])
def test_normalized_weights(weights, expected_weights):
    assert Weightable.normalized_weights(weights) == expected_weights


@pytest.mark.parametrize("weights, expected_percentages", [
    (weights(), [25, 25, 25, 25]),
    (weights_b(), [12.5, 12.5, 25, 50]),
    (weights_c(), [.5/3 * 100, .5/3 * 100, 1/3 * 100, 1/3 * 100]),
    (weights_d(), [10, 30, 60, 0]),
])
def test_weight_percentages(weights, expected_percentages):
    assert Weightable.weight_percentages(weights) == expected_percentages


@pytest.mark.parametrize("weights, expected_fractions", [
    (weights(), [Fraction("1/4"), Fraction("1/4"), Fraction("1/4"), Fraction("1/4")]),
    (weights_b(), [Fraction("1/8"), Fraction("1/8"), Fraction("1/4"), Fraction("1/2")]),
    (weights_c(), [Fraction("1/6"), Fraction("1/6"), Fraction("1/3"), Fraction("1/3")]),
    (weights_d(), [Fraction("1/10"), Fraction("3/10"), Fraction("6/10"), Fraction("0")]),
])
def test_weight_fractions(weights, expected_fractions):
    assert Weightable.weight_fractions(weights) == expected_fractions


@pytest.mark.parametrize("weightable, weight, expected_weights", [
    ([Weightable()], 6, [6]),
    (weightables(), 6, [2, 2, 2]),
    (weightables_nested(), 6, [3, 1, 1, 1]),
    (weightables_double_nested(), 6, [3, 1.5, .5, .5, .5]),
])
def test_set_weight(weightable, weight, expected_weights):

    Weightable.set_weight(weightable, weight)
    weightables = util.flatten(weightable)
    assert [weightable.weight for weightable in weightables] == expected_weights
