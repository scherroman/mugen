from mugen.video.segments.VideoSegment import VideoSegment

from tests import TRACKING_SHOT_VIDEO_PATH, MUSIC_VIDEO_PATH


def get_tracking_shot_segment() -> VideoSegment:
    return VideoSegment(TRACKING_SHOT_VIDEO_PATH)


def get_music_video_segment() -> VideoSegment:
    return VideoSegment(MUSIC_VIDEO_PATH)


def test_video_segment__parses_streams():
    music_video_segment = get_music_video_segment()
    assert len(music_video_segment.streams) == 5
    assert len(music_video_segment.video_streams) == 1
    assert len(music_video_segment.audio_streams) == 1
    assert len(music_video_segment.subtitle_streams) == 3
    assert music_video_segment.video_stream != None
    assert music_video_segment.audio_stream != None
    assert len(music_video_segment.get_subtitle_stream_content(0)) > 0
    assert len(music_video_segment.get_subtitle_stream_content(1)) > 0
    assert len(music_video_segment.get_subtitle_stream_content(2)) > 0
