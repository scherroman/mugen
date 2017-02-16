import moviepy.editor as moviepy

# Project modules
import mugen.settings as s
from mugen.video.VideoSegment import VideoSegment

class MusicVideo(object):
    """
    A music video composed of video segments and audio.

    Attributes:
        videos (list of VideoSegment): List of videos to sample video segments from
        audio (AudioFileClip): Audio for the music video
        video_segments (list of VideoSegment): List of video segments composing the music video
        rejected_video_segments (list of VideoSegment): List of video segments rejected from the music video
    """

    def __init__(self, name, video_files, audio_file, cut_locations=[], dimensions=None, dimensions_type=s.DIMENSIONS_TYPE_WIDESCREEN,
                 crf=s.MOVIEPY_CRF, video_segment_reject_types=s.RS_TYPES_STANDARD):
        """
        Args:
            name (str): The name for the music video
            video_files (list of str): List of video files to sample video segments from
            audio_file (str): Audio file for the music video
            dimensions (int, int): Width and height of the music video
            crf (int): crf quality value of the music video
            video_segment_reject_types (list of str): List of video segment reject types
        """
        self.name = name
        self.video_segments = []
        self.rejected_video_segments = []
        self.videos = [VideoSegment(video_file) for video_file in video_files]
        self.audio = moviepy.AudioFileClip(audio_file)
        self.cut_locations = []
        self.dimensions = self._calculate_music_video_dimensions(dimensions, dimensions_type)
        self.crf = crf
        self.video_segment_reject_types = video_segment_reject_types


    def _calculate_music_video_dimensions(self, dimensions, dimensions_type):


