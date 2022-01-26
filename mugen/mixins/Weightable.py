from copy import deepcopy
from fractions import Fraction
from typing import Optional, Union, List, Any

from mugen import lists
from mugen.lists import MugenList
from mugen.utilities import conversion


class Weightable:
    """
    Mixin for weighting objects, useful for weighted sampling

    Attributes
    ----------
    weight
        assigned weight
    """
    weight: float

    def __init__(self, *args, weight: float = 1, **kwargs):
        super().__init__(*args, **kwargs)

        self.weight = weight


class WeightableList(Weightable, MugenList):
    """
    A list of Weightables with extended functionality
    """

    def __init__(self, weightables: Optional[List[Union[Weightable, List[Any]]]] = None, **kwargs):
        """
        Parameters
        ----------
        weightables
            An arbitrarily nested list of Weightables.
        """
        super().__init__(weightables, **kwargs)

    @property
    def weights(self) -> List[float]:
        return [weightable.weight for weightable in self]

    @property
    def normalized_weights(self) -> List[float]:
        """
        Returns
        -------
        Weights in normalized form, in the range 0-1
        """
        weight_sum = sum(self.weights)

        return [weight / weight_sum for weight in self.weights]

    @property
    def weight_percentages(self) -> List[float]:
        """
        Returns
        -------
        Weights in percentage form, in the range 0-100
        """
        return [weight * 100 for weight in self.normalized_weights]

    @property
    def weight_fractions(self) -> List[Fraction]:
        """
        Returns
        -------
        Weights in simplest fraction form
        """
        return [conversion.float_to_fraction(weight) for weight in self.normalized_weights]

    def flatten(self) -> 'WeightableList':
        """
        Returns
        -------
        A flattened, deep copy of this weightable list, with weights distributed and normalized
        """
        weightables_copy = deepcopy(self)
        self._distribute_weight(weightables_copy, 1)

        return type(self)(lists.flatten(weightables_copy))

    @staticmethod
    def _distribute_weight(weightables: 'WeightableList', weight: float):
        """
        Distributes weight across an arbitrarily nested list of weightables
        """
        normalized_weights = weightables.normalized_weights

        for weightable, normalized_weight in zip(weightables, normalized_weights):
            new_weight = normalized_weight * weight

            if isinstance(weightable, WeightableList):
                WeightableList._distribute_weight(weightable, new_weight)
            else:
                weightable.weight = new_weight
