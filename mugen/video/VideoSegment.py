import random
from collections import OrderedDict

import tesserocr
from PIL import Image
from moviepy.editor import VideoFileClip
from moviepy.video.tools.cuts import detect_scenes

# Project modules
import mugen.settings as s

class VideoSegment(VideoFileClip, object):
    """
    A piece of video
    """

    def __init__(self, src_video_file, src_start_time=None, src_end_time=None, video_traits=None, enable_audio=False):
        super(VideoSegment, self).__init__(src_video_file, audio=enable_audio)
        self.src_video_file = src_video_file
        self.video_traits = []

        if src_start_time and src_end_time:
            self = self.subclip(src_start_time, src_end_time)
        else:
            self.src_start_time = 0
            self.src_end_time = self.duration

        # TODO MAKE INHERENT TO MusicVideo Class
        self.sequence_number = None
        self.video_number = None
        self.beat_interval_numbers = None

    def subclip(self, src_start_time, src_end_time):
        subclip = super(VideoSegment, self).subclip(src_start_time, src_end_time)
        subclip.src_start_time = src_start_time
        subclip.src_end_time = src_end_time

        return subclip

    def random_subclip(self, duration):
        start_time = random.uniform(0, self.duration - duration)
        end_time = start_time + duration

        return self.subclip(start_time, end_time)

    def to_spec(self):
        return OrderedDict([('sequence_number', self.sequence_number),
                            ('video_number', self.video_number),
                            ('video_start_time', self.src_start_time),
                            ('video_end_time', self.src_end_time),
                            ('duration', self.duration),
                            ('beat_interval_numbers', self.beat_interval_numbers)])