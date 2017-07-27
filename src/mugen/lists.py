import collections
from typing import List, Any, Optional as Opt


class MugenList(list):
    """
    A subclass of list with extra functionality, used internally
    """

    def __init__(self, items: Opt[List[Any]] = None):
        if items is None:
            items = []

        super().__init__(items)

    def __add__(self, rhs):
        return type(self)((super().__add__(rhs)))

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        if isinstance(item, slice):
            return type(self)(result)
        else:
            return result

    def pretty_repr(self, item_reprs: List[str] = None):
        if item_reprs is None:
            item_reprs = [repr(item) for item in self]

        repr_str = ""
        for index, element_repr in enumerate(item_reprs):
            if index != 0:
                repr_str += ' '
            repr_str += element_repr
            if index != len(self) - 1:
                repr_str += ', \n'
        return f'[{repr_str}]'

    def lget(self, attr) -> List[Any]:
        """    
        Returns
        -------
        A list of values for the attribute, taken from each element in the array
        """
        return [getattr(elem, attr) for elem in self]

    def flatten(self):
        """
        Returns
        -------
        A new, flattened version of this list.
        Flattens an arbitrarily nested list of objects
        """
        return type(self)(flatten(self))


def flatten(l: List[Any]) -> List[Any]:
    """
    Flattens an arbitrarily nested irregular list of objects
    """
    l_flattened = []

    for element in l:
        if isinstance(element, collections.Iterable) and not isinstance(element, (str, bytes)):
            l_flattened.extend(flatten(element))
        else:
            l_flattened.append(element)

    return l_flattened
