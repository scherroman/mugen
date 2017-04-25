import pytest

from mugen.mixins.Weightable import Weightable


@pytest.fixture
def weights():
    return [1, 1, 1, 1]


@pytest.fixture
def weights_b():
    return [1, 1, 2, 4]


@pytest.fixture
def weights_c():
    return [1/2, 1/2, 1, 1]


@pytest.fixture
def weights_d():
    return [1, 3, 6, 0]


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
