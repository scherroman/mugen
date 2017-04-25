from typing import List, Callable, Optional as Opt, Any, Tuple


class Filter:
    """
    A function used to filter an object based its content
    
    Attributes:
        function: The function to filter with
    """
    function: Callable[..., bool]

    def __init__(self, function: Callable[..., bool]):
        self.function = function

    def __call__(self, *args, **kwargs) -> bool:
        return self.function(*args, **kwargs)


class ContextFilter(Filter):
    """
    A Filter which keeps a running memory of objects to pass to the filter function
    
    Attributes:
        memory: A list of objects to use as memory for the given filter
    
    Requires the filter function to take a 'memory' parameter
    """
    memory: List[Any] = None

    def __init__(self, function, *args, memory: Opt[List[Any]] = None, **kwargs):
        super().__init__(function, *args, **kwargs)

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

    def __init__(self, passed_filters: Opt[List[Filter]] = None,
                 failed_filters: Opt[List[Filter]] = None):
        self.passed_filters = passed_filters or []
        self.failed_filters = failed_filters or []

    def apply_filters(self, filters: List[Filter], short_circuit: bool = True) -> Tuple[List[Filter], List[Filter]]:
        """
        Args:
            filters: Trait filters to test
            short_circuit: Whether or not the function should exit early on a trait filter failure

        Returns: True if all trait_filters passed, false otherwise
        """
        passed_filters = []
        failed_filters = []
        for filter in filters:
            if filter(self):
                passed_filters.append(filter)
            else:
                failed_filters.append(filter)

                if short_circuit:
                    break

        return passed_filters, failed_filters
