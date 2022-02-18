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
    passed_filters, failed_filters = Filterable().apply_filters(filters)
    assert len(passed_filters) == expected_num_passed
    assert len(failed_filters) == expected_num_failed


def test_apply_filters___tests_all_filters_when_short_circuit_is_false():
    passed_filters, failed_filters = Filterable().apply_filters(
        get_failing_filter_combo_short_circuit(), short_circuit=False
    )
    assert len(passed_filters) == 2
    assert len(failed_filters) == 1
