from enum import Enum
from typing import List, Optional, NamedTuple


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
    def aspect_ratio(self):
        return self.width / self.height

def crop_dimensions_to_aspect_ratio(dimensions: Dimensions, desired_aspect_ratio: float) -> Dimensions:
    """
    Returns: dimensions cropped to reach desired aspect ratio
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


def largest_dimensions_for_aspect_ratio(dimensions_list: List[Dimensions],
                                        desired_aspect_ratio: Optional[float]) -> Dimensions:
    """
    Returns: largest dimensions after cropping each dimensions to reach desired aspect ratio
    """
    largest_dimensions = None

    if not dimensions_list:
        raise ValueError(f"{dimensions_list} must not be empty.")

    if desired_aspect_ratio:
        # Find largest dimensions among video segments after resizing each to reach desired aspect ratio
        for dimensions in dimensions_list:
            nearest_dimensions_to_aspect_ratio = crop_dimensions_to_aspect_ratio(dimensions, desired_aspect_ratio)

            if not largest_dimensions:
                largest_dimensions = nearest_dimensions_to_aspect_ratio
            elif nearest_dimensions_to_aspect_ratio.width * nearest_dimensions_to_aspect_ratio.height > \
                                                largest_dimensions.width * largest_dimensions.height:
                largest_dimensions = nearest_dimensions_to_aspect_ratio
    else:
        # Find largest width and height among all dimensions
        largest_width = max((dimensions.width for dimensions in dimensions_list))
        largest_height = max((dimensions.height for dimensions in dimensions_list))

        largest_dimensions = largest_height, largest_width

    return largest_dimensions
