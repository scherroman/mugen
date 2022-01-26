import operator
from typing import List, Callable

import decorator

from mugen.exceptions import ParameterError


def check_if_ranges_overlap(a_start, a_end, b_start, b_end) -> bool:
    """ Checks if two ranges overlap """
    return max(a_start, b_start) < min(a_end, b_end)


def fill_slices(slices: List[slice], length) -> List[slice]:
    """
    Completes the list of slices for a list, given a list of slices and the list's length.
    """
    all_slices = []

    # Sort by start element
    slices_sorted = sorted(slices, key=operator.attrgetter('start'))

    # If any ranges overlap, throw an error
    for index, sl in enumerate(slices_sorted):
        if index == len(slices_sorted) - 1:
            continue

        next_sl = slices_sorted[index + 1]
        if check_if_ranges_overlap(sl.start, sl.stop, next_sl.start, next_sl.stop):
            raise ParameterError(f"Slice ranges may not overlap. "
                                 f"Found overlapping slices {sl}, {next_sl}.")

    for index, sl in enumerate(slices_sorted):
        if index == 0:
            if 0 < sl.start:
                first_sl = slice(0, sl.start)
                all_slices.insert(0, first_sl)

        all_slices.append(sl)

        if index == len(slices_sorted) - 1:
            if sl.stop < length:
                last_sl = slice(sl.stop, length)
                all_slices.append(last_sl)
            continue

        next_sl = slices_sorted[index + 1]
        if sl.stop < next_sl.start:
            new_sl = slice(sl.stop, next_sl.start)
            all_slices.append(new_sl)

    return all_slices


def preprocess_args(func: Callable, variable_names: List[str]):
    """ 
    Applies function to variables in variable_names before launching the function 
    """
    def wrapper(f, *a, **kw):
        func_code = f.__code__

        names = func_code.co_varnames
        new_a = [func(arg) if (name in variable_names) else arg
                 for (arg, name) in zip(a, names)]
        new_kw = {k: func(v) if k in variable_names else v
                  for (k, v) in kw.items()}
        return f(*new_a, **new_kw)

    return decorator.decorator(wrapper)