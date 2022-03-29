import pytest

from mugen.mixins.Filterable import ContextFilter, Filter, Filterable


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
    return (
        has_majority_red_color(x)
        or has_majority_green_color(x)
        or has_majority_blue_color(x)
    )


def get_is_repeat_context_filter():
    return ContextFilter(is_repeat)


def get_has_text_filter():
    return Filter(has_text)


def get_has_majority_red_color_filter():
    return Filter(has_majority_red_color)


def get_has_majority_green_color_filter():
    return Filter(has_majority_green_color)


def get_has_majority_color_filter():
    return Filter(has_majority_color)


def get_failing_filter_combo():
    return [
        get_has_text_filter(),
        get_has_majority_red_color_filter(),
        get_has_majority_green_color_filter(),
    ]


def get_failing_filter_combo_short_circuit():
    return [
        get_has_majority_green_color_filter(),
        get_has_text_filter(),
        get_has_majority_red_color_filter(),
    ]


def get_passing_filter_combo():
    return [
        get_has_text_filter(),
        get_has_majority_color_filter(),
        get_is_repeat_context_filter(),
    ]


@pytest.mark.parametrize(
    "filters, expected_num_passed, expected_num_failed",
    [(get_failing_filter_combo(), 2, 1), (get_passing_filter_combo(), 3, 0)],
)
def test_apply_filters__returns_proper_number_passed_failed(
    filters, expected_num_passed, expected_num_failed
):
    filterable = Filterable()
    filterable.apply_filters(filters)
    assert len(filterable.passed_filters) == expected_num_passed
    assert len(filterable.failed_filters) == expected_num_failed


def test_apply_filters___shorts_circuits_properly():
    filterable = Filterable()
    filterable.apply_filters(get_failing_filter_combo_short_circuit())
    assert len(filterable.passed_filters) == 0
    assert len(filterable.failed_filters) == 1
