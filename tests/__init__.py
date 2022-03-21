import os
from pathlib import Path

MEDIA_PATH = Path(__file__).parent.parent / "media"
IMAGES_PATH = os.path.join(MEDIA_PATH, "images")
VIDEOS_PATH = os.path.join(MEDIA_PATH, "videos")
DETECTION_IMAGES_PATH = os.path.join(IMAGES_PATH, "detection")
DETECTION_VIDEOS_PATH = os.path.join(VIDEOS_PATH, "detection")

NO_BEAT_AUDIO_PATH = os.path.join(MEDIA_PATH, "audio", "no_beat.mp3")
TWO_BEATS_AUDIO_PATH = os.path.join(MEDIA_PATH, "audio", "two_beats.mp3")
LANDSCAPE_IMAGE_PATH = os.path.join(IMAGES_PATH, "landscape.png")
TRACKING_SHOT_VIDEO_PATH = os.path.join(MEDIA_PATH, "videos", "tracking_shot.mp4")
MUSIC_VIDEO_PATH = os.path.join(MEDIA_PATH, "videos", "music_video.mkv")
SPECIAL_CHARACTERS_VIDEO_PATH = os.path.join(
    MEDIA_PATH,
    "videos",
    "loading",
    "special_characters_ '()[]{},;~+-=_&^%$#@!`'.mp4",
)
