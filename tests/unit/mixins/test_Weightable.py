from fractions import Fraction

import pytest

from mugen.mixins.Weightable import Weightable, WeightableList


def get_weightable_list_a():
    return WeightableList(
        [
            Weightable(weight=1),
            Weightable(weight=1),
            Weightable(weight=1),
            Weightable(weight=1),
        ]
    )


def get_weightable_list_b():
    return WeightableList(
        [
            Weightable(weight=1),
            Weightable(weight=1),
            Weightable(weight=2),
            Weightable(weight=4),
        ]
    )


def get_weightable_list_c():
    return WeightableList(
        [
            Weightable(weight=1 / 2),
            Weightable(weight=1 / 2),
            Weightable(weight=1),
            Weightable(weight=1),
        ]
    )


def get_weightable_list_d():
    return WeightableList(
        [
            Weightable(weight=1),
            Weightable(weight=3),
            Weightable(weight=6),
            Weightable(weight=0),
        ]
    )


def get_regular_weightables(weight: float = 1) -> WeightableList:
    return WeightableList(
        [Weightable(weight=2), Weightable(weight=2), Weightable(weight=2)],
        weight=weight,
    )


def get_nested_weightables(weight: float = 1) -> WeightableList:
    return WeightableList(
        [Weightable(weight=3), get_regular_weightables(weight=3)], weight=weight
    )


def get_double_nested_weightables(weight: float = 1) -> WeightableList:
    return WeightableList(
        [Weightable(weight=3), get_nested_weightables(weight=3)], weight=weight
    )


@pytest.mark.parametrize(
    "weightables, expected_weights",
    [
        (get_weightable_list_a(), [1 / 4, 1 / 4, 1 / 4, 1 / 4]),
        (get_weightable_list_b(), [1 / 8, 1 / 8, 2 / 8, 4 / 8]),
        (get_weightable_list_c(), [0.5 / 3, 0.5 / 3, 1 / 3, 1 / 3]),
        (get_weightable_list_d(), [1 / 10, 3 / 10, 6 / 10, 0]),
    ],
)
def test_normalized_weights(weightables, expected_weights):
    assert weightables.normalized_weights == expected_weights


@pytest.mark.parametrize(
    "weightables, expected_percentages",
    [
        (get_weightable_list_a(), [25, 25, 25, 25]),
        (get_weightable_list_b(), [12.5, 12.5, 25, 50]),
        (
            get_weightable_list_c(),
            [0.5 / 3 * 100, 0.5 / 3 * 100, 1 / 3 * 100, 1 / 3 * 100],
        ),
        (get_weightable_list_d(), [10, 30, 60, 0]),
    ],
)
def test_weight_percentages(weightables, expected_percentages):
    assert weightables.weight_percentages == expected_percentages


@pytest.mark.parametrize(
    "weightables, expected_fractions",
    [
        (
            get_weightable_list_a(),
            [Fraction("1/4"), Fraction("1/4"), Fraction("1/4"), Fraction("1/4")],
        ),
        (
            get_weightable_list_b(),
            [Fraction("1/8"), Fraction("1/8"), Fraction("1/4"), Fraction("1/2")],
        ),
        (
            get_weightable_list_c(),
            [Fraction("1/6"), Fraction("1/6"), Fraction("1/3"), Fraction("1/3")],
        ),
        (
            get_weightable_list_d(),
            [Fraction("1/10"), Fraction("3/10"), Fraction("6/10"), Fraction("0")],
        ),
    ],
)
def test_weight_fractions(weightables, expected_fractions):
    assert weightables.weight_fractions == expected_fractions


@pytest.mark.parametrize(
    "weightables, expected_weights",
    [
        (
            get_regular_weightables(),
            [pytest.approx(1 / 3), pytest.approx(1 / 3), pytest.approx(1 / 3)],
        ),
        (
            get_nested_weightables(),
            [
                pytest.approx(1 / 2),
                pytest.approx(1 / 6),
                pytest.approx(1 / 6),
                pytest.approx(1 / 6),
            ],
        ),
        (
            get_double_nested_weightables(),
            [
                pytest.approx(1 / 2),
                pytest.approx(1 / 4),
                pytest.approx(1 / 12),
                pytest.approx(1 / 12),
                pytest.approx(1 / 12),
            ],
        ),
    ],
)
def test_weightable_list(weightables, expected_weights):
    flat_weightables = weightables.flatten()
    assert flat_weightables.weights == expected_weights
