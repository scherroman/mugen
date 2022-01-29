from mugen.video.segments.ImageSegment import ImageSegment

from tests import DATA_PATH


def get_dark_image_segment() -> ImageSegment:
    return ImageSegment(f'{DATA_PATH}/image/dark_image.jpg')
