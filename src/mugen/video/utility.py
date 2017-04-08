import sys

import mugen.constants as c
import mugen.paths as paths
import mugen.utility as util


def reserve_music_video_file(music_video_name):
    util.touch(paths.music_video_output_path(music_video_name))


def seconds_to_time_code(seconds: float) -> str:
    ms = 1000 * round(seconds - int(seconds), 3)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d.%03d" % (h, m, s, ms)


def print_rejected_segment_stats(rejected_segments):
    print("# rejected segment repeats: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == c.VideoTrait.IS_REPEAT])))
    print("# rejected segments with scene changes: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == c.VideoTrait.HAS_SCENE_CHANGE])))
    print("# rejected segments with text detected: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == c.VideoTrait.HAS_TEXT])))
    print("# rejected segments with solid colors: {}"
          .format(len([seg for seg in rejected_segments if seg['reject_type'] == c.VideoTrait.HAS_SOLID_COLOR])))