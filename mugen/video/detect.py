from typing import List, Optional

import pytesseract
from moviepy.video.tools.cuts import detect_scenes
from PIL import Image

from mugen.video.segments.VideoSegment import VideoSegment

DEFAULT_CONTRAST_THRESHOLD = 30


def video_segment_is_repeat(
    video_segment: VideoSegment, video_segments_used: List[VideoSegment]
) -> bool:
    """
    Returns
    -------
    True if a video segment is a repeat of a video segment already used, False otherwise
    """
    for used_segment in video_segments_used:
        if video_segment.overlaps_segment(used_segment):
            return True

    return False


def video_segment_has_cut(video_segment: VideoSegment) -> bool:
    """
    Returns
    -------
    True if a video segment has a cut between shots, False otherwise
    """
    cuts, luminosities = detect_scenes(video_segment, logger=None)

    return len(cuts) > 1


def video_segment_has_text(video_segment: VideoSegment) -> bool:
    """
    Returns
    -------
    True if a video segment has text, False otherwise
    """
    for frame in video_segment.first_middle_last_frames:
        if image_has_text(Image.fromarray(frame)):
            return True

    return False


def video_segment_has_low_contrast(
    video_segment: VideoSegment, *args, **kwargs
) -> bool:
    """
    Returns
    -------
    True if a video segment has low contrast (solid color, dark scene, etc...), False otherwise
    """
    for frame in video_segment.first_middle_last_frames:
        if image_has_low_contrast(Image.fromarray(frame), *args, **kwargs):
            return True

    return False


def image_has_text(image: Image):
    """
    Parameters
    ----------
    image
        A Pillow image

    Returns
    -------
    True if the image has text, False otherwise
    """
    text = pytesseract.image_to_string(image)
    return True if len(text.strip()) > 0 else False


def image_has_low_contrast(
    image: Image, threshold: Optional[float] = DEFAULT_CONTRAST_THRESHOLD
) -> bool:
    """
    Parameters
    ----------
    image
        A Pillow image

    threshold
        The maximum difference in luma that is considered low contrast

    Returns
    -------
    True if the image has low contrast, False otherwise
    """
    # Convert the image to grayscale, find the difference in luma
    extrema = image.convert("L").getextrema()
    return True if abs(extrema[1] - extrema[0]) <= threshold else False
