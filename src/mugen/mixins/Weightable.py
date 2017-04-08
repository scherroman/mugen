import copy
from typing import Optional as Opt, Union, List


class Weightable:
    """
    Mixin for weighting objects, useful for weighted sampling
    """
    _weight: float = 1

    def __init__(self, weight: Opt[float] = None):
        if weight is not None:
            self.weight = weight

    @staticmethod
    def normalized_weights(weights: List[float]) -> List[float]:
        """
        Returns: Weights in normalized form, in the range 0-1
        """
        weight_sum = sum(weights)

        return [weight / weight_sum for weight in weights]

    @staticmethod
    def weight_percentages(weights: List[float]) -> List[float]:
        """
        Returns: Weights in percentage form, in the range 0-100
        """
        normalized_weights = Weightable.normalized_weights(weights)

        return [weight * 100 for weight in normalized_weights]




