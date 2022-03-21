import os

import pytest
from PIL import Image

from mugen.utilities import system
from mugen.video import detect
from mugen.video.segments.VideoSegment import VideoSegment
from tests import DETECTION_IMAGES_PATH, DETECTION_VIDEOS_PATH

LOW_CONTRAST_TEST_IMAGES_PATH = os.path.join(DETECTION_IMAGES_PATH, "low_contrast")
TEXT_TEST_IMAGES_PATH = os.path.join(DETECTION_IMAGES_PATH, "text")
CUT_TEST_VIDEO_SEGMENTS_PATH = os.path.join(DETECTION_VIDEOS_PATH, "cut")
PRECISE_CUT_VIDEO_PATH = os.path.join(CUT_TEST_VIDEO_SEGMENTS_PATH, "precise_cut.mp4")

image_files_with_low_contrast = system.list_directory_files(
    os.path.join(LOW_CONTRAST_TEST_IMAGES_PATH, "true")
)
image_files_without_low_contrast = system.list_directory_files(
    os.path.join(LOW_CONTRAST_TEST_IMAGES_PATH, "false")
)
video_files_with_low_contrast = system.list_directory_files(
    os.path.join(DETECTION_VIDEOS_PATH, "low_contrast", "true")
)
image_files_with_text = system.list_directory_files(
    os.path.join(TEXT_TEST_IMAGES_PATH, "true")
)
image_files_without_text = system.list_directory_files(
    os.path.join(TEXT_TEST_IMAGES_PATH, "false")
)
video_segment_files_with_cuts = system.list_directory_files(
    os.path.join(CUT_TEST_VIDEO_SEGMENTS_PATH, "true")
)
video_segment_files_without_cuts = system.list_directory_files(
    os.path.join(CUT_TEST_VIDEO_SEGMENTS_PATH, "false")
)


@pytest.mark.parametrize("file", image_files_with_low_contrast)
def test_image_has_low_contrast__detects_low_contrast_when_there_is_low_contrast(file):
    assert detect.image_has_low_contrast(Image.open(file)) is True


@pytest.mark.parametrize("file", image_files_without_low_contrast)
def test_image_has_low_contrast__does_not_detect_low_contrast_when_there_is_no_low_contrast(
    file,
):
    assert detect.image_has_low_contrast(Image.open(file)) is False


@pytest.mark.parametrize("file", video_files_with_low_contrast)
def test_video_segment_has_low_contrast__detects_low_contrast_on_black_start_and_ends(
    file,
):
    assert detect.video_segment_has_low_contrast(VideoSegment(file)) is True


@pytest.mark.parametrize("file", image_files_with_text)
def test_image_has_text__detects_text_when_there_is_text(file):
    assert detect.image_has_text(Image.open(file)) is True


@pytest.mark.parametrize("file", image_files_without_text)
def test_image_has_text__does_not_detect_text_when_there_is_no_text(file):
    assert detect.image_has_text(Image.open(file)) is False


@pytest.mark.parametrize("file", video_segment_files_with_cuts)
def test_video_segment_has_cut__detects_cut_when_there_is_a_cut(file):
    assert detect.video_segment_has_cut(VideoSegment(file)) is True


@pytest.mark.parametrize("file", video_segment_files_without_cuts)
def test_video_segment_has_cut__does_not_detect_cut_when_there_is_no_cut(file):
    assert detect.video_segment_has_cut(VideoSegment(file)) is False


def test_video_segment_has_cut__detects_cut_in_precise_time_range_correctly():
    # Cut is at time ~4.5 seconds
    segment_with_cut_at_very_end = VideoSegment(PRECISE_CUT_VIDEO_PATH).subclip(
        1.6, 4.6
    )
    # Cut is at time ~1.0 seconds
    segment_with_cut_at_very_beginning = VideoSegment(PRECISE_CUT_VIDEO_PATH).subclip(
        0.9, 3.9
    )
    assert detect.video_segment_has_cut(segment_with_cut_at_very_end) is True
    assert detect.video_segment_has_cut(segment_with_cut_at_very_beginning) is True
