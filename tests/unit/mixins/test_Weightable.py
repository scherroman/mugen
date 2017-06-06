from fractions import Fraction
from typing import List, Any

import pytest

from mugen.mixins.Weightable import Weightable, WeightableList


@pytest.fixture
def weightable_list_a() -> WeightableList:
    return WeightableList([Weightable(), Weightable(), Weightable(), Weightable()], weights=[1, 1, 1, 1])


@pytest.fixture
def weightable_list_b() -> WeightableList:
    return WeightableList([Weightable(), Weightable(), Weightable(), Weightable()], weights=[1, 1, 2, 4])


@pytest.fixture
def weightable_list_c() -> WeightableList:
    return WeightableList([Weightable(), Weightable(), Weightable(), Weightable()], weights=[1/2, 1/2, 1, 1])


@pytest.fixture
def weightable_list_d() -> WeightableList:
    return WeightableList([Weightable(), Weightable(), Weightable(), Weightable()], weights=[1, 3, 6, 0])


@pytest.fixture
def weightable() -> Weightable:
    return Weightable()


@pytest.fixture
def weightables_regular() -> List[Weightable]:
    return [Weightable(), Weightable(), Weightable()]


@pytest.fixture
def weightables_nested() -> List[Any]:
    return [weightable(), weightables_regular()]


@pytest.fixture
def weightables_double_nested() -> List[Any]:
    return [weightable(), [weightable(), weightables_regular()]]


@pytest.mark.parametrize("weightables, expected_weights", [
    (weightable_list_a(), [1 / 4, 1 / 4, 1 / 4, 1 / 4]),
    (weightable_list_b(), [1 / 8, 1 / 8, 2 / 8, 4 / 8]),
    (weightable_list_c(), [.5 / 3, .5 / 3, 1 / 3, 1 / 3]),
    (weightable_list_d(), [1 / 10, 3 / 10, 6 / 10, 0]),
])
def test_normalized_weights(weightables, expected_weights):
    assert weightables.normalized_weights == expected_weights


@pytest.mark.parametrize("weightables, expected_percentages", [
    (weightable_list_a(), [25, 25, 25, 25]),
    (weightable_list_b(), [12.5, 12.5, 25, 50]),
    (weightable_list_c(), [.5 / 3 * 100, .5 / 3 * 100, 1 / 3 * 100, 1 / 3 * 100]),
    (weightable_list_d(), [10, 30, 60, 0]),
])
def test_weight_percentages(weightables, expected_percentages):
    assert weightables.weight_percentages == expected_percentages


@pytest.mark.parametrize("weightables, expected_fractions", [
    (weightable_list_a(), [Fraction("1/4"), Fraction("1/4"), Fraction("1/4"), Fraction("1/4")]),
    (weightable_list_b(), [Fraction("1/8"), Fraction("1/8"), Fraction("1/4"), Fraction("1/2")]),
    (weightable_list_c(), [Fraction("1/6"), Fraction("1/6"), Fraction("1/3"), Fraction("1/3")]),
    (weightable_list_d(), [Fraction("1/10"), Fraction("3/10"), Fraction("6/10"), Fraction("0")]),
])
def test_weight_fractions(weightables, expected_fractions):
    assert weightables.weight_fractions == expected_fractions


@pytest.mark.parametrize("weightables, weights, expected_weights", [
    (weightables_regular(), [2, 2, 2], [2, 2, 2]),
    (weightables_nested(), [3, 3], [3, 1, 1, 1]),
    (weightables_double_nested(), [3, 3, 3], [3, 1.5, .5, .5, .5]),
])
def test_weightable_list(weightables, weights, expected_weights):
    weightable_list = WeightableList(weightables, weights)
    assert weightable_list.weights == expected_weights
