import json
from typing import List

import pytesseract
from moviepy.video.tools.cuts import detect_scenes
from PIL import Image

from mugen.utilities import system
from mugen.video.segments.VideoSegment import VideoSegment

LOW_CONTRAST_THRESHOLD = 45
FFPROBE_CUT_DETECTION_THRESHOLD = 0.09


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
    cut_is_detected_by_moviepy = check_if_moviepy_detects_cut(video_segment)

    # To reduce false positives, check if ffprobe agrees using a low threshold
    cut_is_detected_by_ffprobe = False
    if cut_is_detected_by_moviepy:
        cut_is_detected_by_ffprobe = check_if_ffprobe_detects_cut(video_segment)

    return cut_is_detected_by_moviepy and cut_is_detected_by_ffprobe


def check_if_moviepy_detects_cut(video_segment: VideoSegment) -> bool:
    cuts, _ = detect_scenes(video_segment, logger=None)
    return len(cuts) > 1


def check_if_ffprobe_detects_cut(video_segment: VideoSegment) -> bool:
    escaped_file_name = video_segment.file.replace("'", r"'\\\''")
    # It is important to use all of the options seek_point, trim start, and trim end/duration to precisely target the detection area
    # seek_point makes the detection fast by skipping to the approximate start point
    # trim start and end/duration keeps the start point and end points precise
    result = system.run_command(
        [
            "ffprobe",
            "-print_format",
            "json",
            "-show_frames",
            "-f",
            "lavfi",
            f"movie='{escaped_file_name}':seek_point={video_segment.source_start_time},trim={video_segment.source_start_time}:duration={video_segment.duration},select=gt(scene\\,{FFPROBE_CUT_DETECTION_THRESHOLD})",
        ]
    )
    frames = json.loads(result.stdout).get("frames", [])

    return len(frames) > 0


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


def image_has_low_contrast(image: Image) -> bool:
    """
    Parameters
    ----------
    image
        A Pillow image

    Returns
    -------
    True if the image has low contrast, False otherwise
    """
    # Convert the image to grayscale, find the difference in luma
    extrema = image.convert("L").getextrema()
    return True if abs(extrema[1] - extrema[0]) <= LOW_CONTRAST_THRESHOLD else False
