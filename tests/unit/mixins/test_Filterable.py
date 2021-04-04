import pytest

from mugen.mixins.Filterable import Filterable, Filter, ContextFilter


def is_repeat(x, memory):
    return True


def has_text(x):
    return True


def has_majority_red_color(x):
    return True


def has_majority_green_color(x):
    return False


def has_majority_blue_color(x):
    return False


def has_majority_color(x):
    return has_majority_red_color(x) or has_majority_green_color(x) or has_majority_blue_color(x)


@pytest.fixture
def context_filter_is_repeat():
    return ContextFilter(is_repeat)


@pytest.fixture
def filter_has_text():
    return Filter(has_text)


@pytest.fixture
def filter_has_majority_red_color():
    return Filter(has_majority_red_color)


@pytest.fixture
def filter_has_majority_green_color():
    return Filter(has_majority_green_color)


@pytest.fixture
def filter_has_majority_blue_color():
    return Filter(has_majority_blue_color)


@pytest.fixture
def filter_has_majority_color():
    return Filter(has_majority_color)


@pytest.fixture
def failing_filter_combo():
    return [filter_has_text(), filter_has_majority_red_color(), filter_has_majority_green_color()]


@pytest.fixture
def failing_filter_combo_shortcircuit():
    return [filter_has_majority_green_color(), filter_has_text(), filter_has_majority_red_color()]


@pytest.fixture
def passing_filter_combo():
    return [filter_has_text(), filter_has_majority_color(), context_filter_is_repeat()]


@pytest.fixture
def filterable():
    return Filterable()


""" TESTS """


@pytest.mark.parametrize("filters, expected_num_passed, expected_num_failed", [
    (failing_filter_combo(), 2, 1),
    (passing_filter_combo(), 3, 0)
])
def test_apply_filters__returns_proper_number_passed_failed(filterable, filters, expected_num_passed,
                                                            expected_num_failed):
    passed_filters, failed_filters = filterable.apply_filters(filters)
    assert len(passed_filters) == expected_num_passed
    assert len(failed_filters) == expected_num_failed


def test_apply_filters___tests_all_filters_when_short_circuit_is_false(filterable, failing_filter_combo_shortcircuit):
    passed_filters, failed_filters = filterable.apply_filters(failing_filter_combo_shortcircuit, short_circuit=False)
    assert len(passed_filters) == 2
    assert len(failed_filters) == 1


# def test_context_filter__throws_exception_when_filter_has_no_memory_parameter():
#     with pytest.raises(ValueError):
#         ContextFilter(has_text)



