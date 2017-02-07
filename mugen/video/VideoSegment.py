from moviepy.editor import VideoFileClip

class VideoSegment(VideoFileClip, object):
    '''A video segment that composes part of a music video'''

    def __init__(self, src_video_file, enable_audio=False):
        super(VideoSegment, self).__init__(src_video_file, audio=enable_audio)
        self.src_video_file = src_video_file

    def subclip(self, t_start=0, t_end=None):
        subclip = super(VideoSegment, self).subclip(t_start, t_end)
        subclip.src_start_time = t_start
        subclip.src_end_time = t_end

        return subclip



