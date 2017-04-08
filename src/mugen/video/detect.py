import tesserocr
from typing import List, Optional as Opt

from PIL import Image
from moviepy.video.tools.cuts import detect_scenes

from mugen.video.constants import LIST_3D
import mugen.video.VideoSegment as VideoSegment

DEFAULT_CONTRAST_THRESHOLD = 30


def video_segment_is_repeat(video_segment: VideoSegment, video_segments_used: List[VideoSegment]) -> bool:
    """
    Returns: True if a video segment is a repeat of a video segment already used, False otherwise
    """
    for used_segment in video_segments_used:
        if video_segment.overlaps_segment(used_segment):
            return True

    return False


def video_segment_has_cut(video_segment: VideoSegment) -> bool:
    """
    Returns: True if a video segment contains a cut between shots, False otherwise
    """
    cuts, luminosities = detect_scenes(video_segment, progress_bar=False)

    return len(cuts) > 1


def video_segment_has_text(video_segment: VideoSegment) -> bool:
    """
    Returns: True if a video segment contains text, False otherwise
    """
    for frame in video_segment.first_middle_last_frames:
        if image_has_text(frame):
            return True

    return False


def video_segment_has_low_contrast(video_segment: VideoSegment, *args, **kwargs) -> bool:
    """        
    Returns: True if a video segment has low contrast, False otherwise
    """
    for frame in video_segment.first_middle_last_frames:
        if image_has_low_contrast(frame, *args, **kwargs):
            return True

    return False


def image_has_text(image: LIST_3D):
    """
    Args:
        image: A 3D array with the RGB values for the image

    Returns: True if the image contains text, False otherwise
    """
    image = Image.fromarray(image)
    text = tesserocr.image_to_text(image)

    return True if len(text.strip()) > 0 else False


def image_has_low_contrast(image: LIST_3D, threshold: Opt[float] = DEFAULT_CONTRAST_THRESHOLD) -> bool:
    """
    Args:
        image: A 3D array with the RGB values for the image
        threshold: The maximum difference in luma that is considered low contrast

    Returns: True if the image has low contrast, False otherwise
    """
    # Convert the image to grayscale, find the difference in luma
    image = Image.fromarray(image)
    extrema = image.convert("L").getextrema()

    return True if abs(extrema[1] - extrema[0]) <= threshold else False