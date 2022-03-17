from mugen.video.segments.ImageSegment import ImageSegment
from tests import LANDSCAPE_IMAGE_PATH


def get_landscape_image_segment() -> ImageSegment:
    return ImageSegment(LANDSCAPE_IMAGE_PATH)
