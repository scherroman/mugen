from fractions import Fraction
from typing import Optional as Opt, Union, List, Any

from mugen import utility as util


class Weightable:
    """
    Mixin for weighting objects, useful for weighted sampling
    """
    weight: float = 1

    def __init__(self, *args, weight: Opt[float] = None, **kwargs):
        if weight is not None:
            self.weight = weight

    @staticmethod
    def normalized_weights(weights: List[float]) -> List[float]:
        """
        Returns
        -------
        Weights in normalized form, in the range 0-1
        """
        weight_sum = sum(weights)

        return [weight / weight_sum for weight in weights]

    @staticmethod
    def weight_percentages(weights: List[float]) -> List[float]:
        """
        Returns
        -------
        Weights in percentage form, in the range 0-100
        """
        normalized_weights = Weightable.normalized_weights(weights)

        return [weight * 100 for weight in normalized_weights]

    @staticmethod
    def weight_fractions(weights: List[float]) -> List[Fraction]:
        """
        Returns
        -------
        Weights in percentage form, in the range 0-100
        """
        normalized_weights = Weightable.normalized_weights(weights)

        return [util.float_to_fraction(weight) for weight in normalized_weights]

    @staticmethod
    def _distribute_weight(weightables: List[Union['Weightable', List[Any]]], weight: float):
        """
        Evenly distributes weight across an arbitrarily nested irregular list of weightables
        """
        split_weight = weight / len(weightables)

        for weightable in weightables:
            if type(weightable) is list:
                Weightable._distribute_weight(weightable, split_weight)
            else:
                weightable.weight = split_weight

    @staticmethod
    def set_weight(weightable: Union['Weightable', List[Any]], weight):
        """
        Sets the weight for a weightable, 
        or evenly distributes the weight across an arbitrarily nested irregular list of weightables
        """
        if type(weightable) is list:
            Weightable._distribute_weight(weightable, weight)
        else:
            weightable.weight = weight
