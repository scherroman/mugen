from enum import Enum
from typing import List, NamedTuple, Union, Any, Tuple

_sentinel = object()


class AspectRatio(float, Enum):
    FULLSCREEN = 4 / 3
    WIDESCREEN = 16 / 9
    ULTRAWIDE = 21 / 9


class DimensionsBase(NamedTuple):
    width: int
    height: int


class Dimensions(DimensionsBase):
    __slots__ = ()

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height

    @property
    def resolution(self) -> int:
        return self.width * self.height


def crop_dimensions_to_aspect_ratio(dimensions: Dimensions, desired_aspect_ratio: float) -> Dimensions:
    """
    Returns
    -------
    Dimensions cropped to reach desired aspect ratio
    """
    nearest_dimensions_to_aspect_ratio = dimensions

    if dimensions.aspect_ratio > desired_aspect_ratio:
        # Crop sides
        cropped_width = int(desired_aspect_ratio * dimensions.height)
        nearest_dimensions_to_aspect_ratio = Dimensions(cropped_width, dimensions.height)
    elif dimensions.aspect_ratio < desired_aspect_ratio:
        # Crop top & bottom
        cropped_height = int(dimensions.width / desired_aspect_ratio)
        nearest_dimensions_to_aspect_ratio = Dimensions(dimensions.width, cropped_height)

    return nearest_dimensions_to_aspect_ratio


def crop_coordinates_for_aspect_ratio(dimensions: Dimensions, desired_aspect_ratio: float) -> Tuple[int, int, int, int]:
    """
    Returns
    -------
    Coordinates at which to crop the given dimensions to reach the desired aspect ratio. 
    x1, y1, x2, y2 -> (x1, y1) for the top left corner, (x2, y2) for the bottom right corner 
    """
    x1 = 0
    y1 = 0
    x2 = dimensions.width
    y2 = dimensions.height

    if dimensions.aspect_ratio > desired_aspect_ratio:
        # Crop sides
        cropped_width = int(desired_aspect_ratio * dimensions.height)
        width_difference = dimensions.width - cropped_width
        x1 = width_difference / 2
        x2 = dimensions.width - width_difference / 2
    elif dimensions.aspect_ratio < desired_aspect_ratio:
        # Crop top & bottom
        cropped_height = int(dimensions.width / desired_aspect_ratio)
        height_difference = dimensions.height - cropped_height
        y1 = height_difference / 2
        y2 = dimensions.height - height_difference / 2

    return x1, y1, x2, y2


def largest_dimensions_for_aspect_ratio(dimensions_list: List[Dimensions], desired_aspect_ratio: float,
                                        default: Any = _sentinel) -> Union[Dimensions, Any]:
    """
    Returns
    -------
    The largest dimensions after cropping each dimensions to reach desired aspect ratio
    """
    if not dimensions_list:
        if default is not _sentinel:
            return default
        raise ValueError(f"{dimensions_list} must not be empty.")

    largest_dimensions = crop_dimensions_to_aspect_ratio(dimensions_list[0], desired_aspect_ratio)
    for dimensions in dimensions_list[1:]:
        nearest_dimensions_to_aspect_ratio = crop_dimensions_to_aspect_ratio(dimensions, desired_aspect_ratio)

        if nearest_dimensions_to_aspect_ratio.resolution > largest_dimensions.resolution:
            largest_dimensions = nearest_dimensions_to_aspect_ratio

    return largest_dimensions


