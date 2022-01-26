import json
from functools import wraps
from fractions import Fraction

from mugen.utilities.general import preprocess_args


def ensure_json_serializable(*dictionaries: dict):
    """
    Decorator ensures dictionaries are json serializable
    """
    def _ensure_json_serializable(dictionary):
        try:
            json.dumps(dictionary)
        except TypeError as error:
            print(f"{dictionary} is not json serializable. Error: {error}")
            raise

        return dictionary

    return preprocess_args(_ensure_json_serializable, *dictionaries)


def validate_speed_multiplier(func):
    """
    Decorator validates speed multiplier and speed_multiplier_offset values
    """

    @wraps(func)
    def _validate_speed_multiplier(*args, **kwargs):
        speed_multiplier = kwargs.get('speed_multiplier')
        speed_multiplier_offset = kwargs.get('speed_multiplier_offset')

        if speed_multiplier:
            speed_multiplier = Fraction(speed_multiplier).limit_denominator()
            if speed_multiplier == 0 or (speed_multiplier.numerator != 1 and speed_multiplier.denominator != 1):
                raise ValueError(f"""Improper speed multiplier {speed_multiplier}. 
                                     Speed multipliers must be of the form x or 1/x, where x is a natural number.""")

        if speed_multiplier_offset:
            if speed_multiplier >= 1:
                raise ValueError(f"""Improper speed multiplier offset {speed_multiplier_offset} for speed multiplier
                                     {speed_multiplier}. Speed multiplier offsets may only be used with slowdown speed
                                     multipliers.""")
            elif speed_multiplier_offset > speed_multiplier.denominator - 1:
                raise ValueError(f"""Improper speed multiplier offset {speed_multiplier_offset} for speed multiplier
                                     {speed_multiplier}. Speed multiplier offset may not be greater than x - 1 for a 
                                     slowdown of 1/x.""")

        return func(*args, **kwargs)

    return _validate_speed_multiplier
