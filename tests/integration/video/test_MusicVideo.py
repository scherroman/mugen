import os

from mugen import MusicVideo
from mugen.utilities import system
from mugen.video.filters import VideoFilter
from tests.integration.video.segments.test_ImageSegment import (
    get_landscape_image_segment,
)
from tests.integration.video.segments.test_VideoSegment import get_tracking_shot_segment
from tests.unit.video.segments.test_ColorSegment import get_orange_segment


def get_basic_music_video() -> MusicVideo:
    short_tracking_shot_segment = get_tracking_shot_segment().subclip(end_time=1)
    return MusicVideo(
        [
            short_tracking_shot_segment,
            get_landscape_image_segment(),
            get_orange_segment(),
        ]
    )


def test_music_video__writes_to_file():
    music_video_path = get_basic_music_video().write_to_video_file(show_progress=False)
    assert os.path.isfile(music_video_path)


def test_music_video__saves_and_loads():
    music_video = get_basic_music_video()
    music_video_file = music_video.save()
    loaded_music_video = MusicVideo.load(music_video_file)

    assert len(loaded_music_video.segments) == len(music_video.segments)


def test_music_video__saves_segments(tmp_path):
    music_video = get_basic_music_video()
    segments_path = os.path.join(tmp_path, "music_video")
    music_video.write_video_segments(segments_path)

    segment_files = system.list_directory_files(
        os.path.join(segments_path, "video_segments")
    )

    assert len(segment_files) == len(music_video.segments)


def test_music_video__saves_rejected_segments(tmp_path):
    music_video = get_basic_music_video()
    landscape_image = get_landscape_image_segment()
    orange_segment = get_orange_segment()
    landscape_image.failed_filters = [VideoFilter.not_has_low_contrast]
    orange_segment.failed_filters = [VideoFilter.not_has_low_contrast]
    music_video.rejected_segments = [landscape_image, orange_segment]

    rejected_segments_path = os.path.join(tmp_path, "music_video")
    music_video.write_rejected_video_segments(rejected_segments_path)

    segment_files = system.list_directory_files(
        os.path.join(
            rejected_segments_path, "rejected_video_segments", "not_has_low_contrast"
        )
    )

    assert len(segment_files) == len(music_video.rejected_segments)
