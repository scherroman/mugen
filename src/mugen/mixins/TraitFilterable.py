from typing import List, NamedTuple, Callable, Optional as Opt


class TraitFilter(NamedTuple):
    """
    trait: Descriptive name for the filter i.e. "IS_...", "HAS_..."
    filter: The function to filter with
    """
    trait: str
    filter: Callable[..., bool]


class TraitFilterable:
    """
    Mixin for running filters against an object and caching the results
    """
    passed_trait_filters: List[TraitFilter]
    failed_trait_filters: List[TraitFilter]

    def __init__(self, passed_trait_filters: Opt[List[TraitFilter]] = None,
                 failed_trait_filters: Opt[List[TraitFilter]] = None):
        self.passed_trait_filters = passed_trait_filters or []
        self.failed_trait_filters = failed_trait_filters or []

    def passes_trait_filters(self, trait_filters: List[TraitFilter], exit_on_fail: bool = True) -> bool:
        """
        Args:
            trait_filters: Trait filters to test
            exit_early: Whether or not the function should exit early on a trait filter failure

        Returns: True if all trait_filters passed, false otherwise
        """
        passed_trait_filters = []
        failed_trait_filters = []
        for trait_filter in trait_filters:
            if trait_filter.filter(self):
                passed_trait_filters.append(trait_filter)
            else:
                failed_trait_filters.append(trait_filter)

                if exit_on_fail:
                    break

        self.passed_trait_filters.extend(passed_trait_filters)
        self.failed_trait_filters.extend(failed_trait_filters)

        return not failed_trait_filters

    def clear_trait_filter_results(self):
        self.passed_trait_filters.clear()
        self.failed_trait_filters.clear()
