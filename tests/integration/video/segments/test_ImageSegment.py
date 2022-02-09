from mugen.video.segments.ImageSegment import ImageSegment

from tests import DARK_IMAGE_PATH


def get_dark_image_segment() -> ImageSegment:
    return ImageSegment(DARK_IMAGE_PATH)
