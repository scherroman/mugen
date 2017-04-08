import pytest

from mugen.mixins.TraitFilterable import TraitFilterable, TraitFilter


def has_text(x):
    return True


def has_majority_red_color(x):
    return True


def has_majority_green_color(x):
    return False


def has_majority_blue_color(x):
    return False


@pytest.fixture
def trait_filter_has_text():
    return TraitFilter("has_text", has_text)


@pytest.fixture
def trait_filter_has_majority_red_color():
    return TraitFilter("has_majority_red_color", has_majority_red_color)


@pytest.fixture
def trait_filter_has_majority_green_color():
    return TraitFilter("has_majority_green_color", has_majority_green_color)


@pytest.fixture
def trait_filter_has_majority_blue_color():
    return TraitFilter("has_majority_blue_color", has_majority_blue_color)


@pytest.fixture
def trait_filter_has_majority_color():
    return TraitFilter("has_majority_color", lambda x: has_majority_red_color(x) or has_majority_green_color(x) or
                                                       has_majority_blue_color(x))


@pytest.fixture
def failing_trait_filter_combo():
    return [trait_filter_has_text(), trait_filter_has_majority_red_color(), trait_filter_has_majority_green_color()]


@pytest.fixture
def failing_trait_filter_combo_fail_first():
    return [trait_filter_has_majority_green_color(), trait_filter_has_text(), trait_filter_has_majority_red_color()]


@pytest.fixture
def passing_trait_filter_combo():
    return [trait_filter_has_text(), trait_filter_has_majority_color()]


@pytest.fixture
def trait_filterable():
    return TraitFilterable()


@pytest.mark.parametrize("trait_filters, expected", [
    (failing_trait_filter_combo(), False),
    (passing_trait_filter_combo(), True)
])
def test_passes_trait_filters(trait_filterable, trait_filters, expected):
    assert trait_filterable.passes_trait_filters(trait_filters) is expected


@pytest.mark.parametrize("trait_filters, expected, expected_b", [
    (failing_trait_filter_combo(), 2, 1),
    (passing_trait_filter_combo(), 2, 0)
])
def test_passes_trait_filters___saves_passed_and_failed_trait_filters(trait_filterable, trait_filters, expected,
                                                                      expected_b):
    trait_filterable.passes_trait_filters(trait_filters)
    assert len(trait_filterable.passed_trait_filters) == expected
    assert len(trait_filterable.failed_trait_filters) == expected_b


def test_passes_trait_filters___tests_all_filters_when_exit_on_fail_is_false(trait_filterable,
                                                                             failing_trait_filter_combo_fail_first):
    trait_filterable.passes_trait_filters(failing_trait_filter_combo_fail_first, exit_on_fail=False)
    assert len(trait_filterable.passed_trait_filters) == 2
    assert len(trait_filterable.failed_trait_filters) == 1


def test_clear_trait_filter_results(trait_filterable, failing_trait_filter_combo):
    trait_filterable.passes_trait_filters(failing_trait_filter_combo)
    trait_filterable.clear_trait_filter_results()
    assert len(trait_filterable.passed_trait_filters) == 0
    assert len(trait_filterable.failed_trait_filters) == 0



