from typing import Any, Callable, List, Optional, Tuple


class Filter:
    """
    A function used to filter an object based its sources

    Attributes
    ----------
    name
        Name of the filter function

    function
        The function to filter with
    """

    name: str
    function: Callable[..., bool]

    def __init__(self, function: Callable[..., bool]):
        self.name = function.__name__
        self.function = function

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __call__(self, *args, **kwargs) -> bool:
        return self.function(*args, **kwargs)


class ContextFilter(Filter):
    """
    A Filter which keeps a running memory of objects to pass to the filter function

    Attributes
    ----------
    memory
        A list of objects to use as memory for the given filter

    Requires the filter function to take a 'memory' parameter
    """

    memory: List[Any] = None

    def __init__(self, function, memory: Optional[List[Any]] = None):
        super().__init__(function)

        if memory:
            self.memory = memory

    def __call__(self, *args, **kwargs) -> bool:
        return self.function(*args, memory=self.memory, **kwargs)


class Filterable:
    """
    Mixin for running filters against an object and caching the results
    """

    passed_filters: List[Filter]
    failed_filters: List[Filter]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_filters = []
        self.failed_filters = []

    def apply_filters(self, filters: List[Filter]) -> Tuple[List[Filter], List[Filter]]:
        """
        Tests this object against a set of filters, short circuiting if any of the filters fail

        Parameters
        ----------
        filters
            Filters to test

        Returns
        -------
        True if all filters passed, false otherwise
        """
        for filter in filters:
            if filter(self):
                self.passed_filters.append(filter)
            else:
                self.failed_filters.append(filter)
                break
