from typing import List, NamedTuple, Callable

class TraitFilter(NamedTuple):
    """
    trait: Descriptive name for the filter i.e. "IS_...", "HAS_..."
    filter: The function to filter with
    """
    trait: str
    filter: Callable[..., bool]

class TraitFilterable:
    """
    Mixin for filtering and caching the results
    """
    def __init__(self):
        self.has_been_trait_filtered = False
        self.passed_trait_filters = []
        self.failed_trait_filters = []

    @property
    def has_passed_all_trait_filters(self):
        return not self.failed_trait_filters

    def passes_trait_filters(self, trait_filters: List[TraitFilter], exit_early: bool = True):
        """
        Args:
            trait_filters: List of trait filters to test
            exit_early: Whether or not the function should exit early on a trait filter failure

        Returns: True if all trait_filters passed, false otherwise
        """
        self.has_been_trait_filtered = True

        passed_trait_filters = []
        failed_trait_filters = []
        for trait_filter in trait_filters:
            if trait_filter.filter(self):
                passed_trait_filters.append(trait_filter)
            else:
                failed_trait_filters.append(trait_filter)

                if exit_early:
                    break

        self.passed_trait_filters.extend(passed_trait_filters)
        self.failed_trait_filters.extend(failed_trait_filters)

        return not failed_trait_filters

    def clear_trait_filter_results(self):
        self.passed_trait_filters.clear()
        self.failed_trait_filters.clear()
        self.has_been_trait_filtered = False
