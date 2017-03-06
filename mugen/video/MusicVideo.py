from moviepy.editor import VideoClip

# Project modules
import mugen.constants as c
import mugen.video.sizing as v_sizing

class MusicVideo(object):
    """
    A music video composed of video segments and audio.

    Attributes:
        source_videos (VideoSet): Videos used to sample video segments from
        video_segments (list of VideoSegment): Video segments composing the music video
        video_segment_rejects (list of VideoSegment): Video segments rejected from the music video
        audio (AudioFileClip): Audio for the music video
        _dimensions (int, int): Width and height for the music video
        aspect_ratio (int, int): Aspect ratio for the music video (Overruled if _dimensions is set)
        crf (int): crf quality value for the music video
        cutting_method (dict): Json Serializable dictionary describing method used to determine cut locations
    """

    def __init__(self, source_videos, video_segments, audio, video_segment_rejects=None, dimensions=None,
                 aspect_ratio=v_sizing.AspectRatio.WIDESCREEN, crf=c.DEFAULT_VIDEO_CRF, cutting_method=None):
        # Required Parameters
        self.source_videos = source_videos
        self.video_segments = video_segments
        self.audio = audio

        # Optional Parameters
        self.crf = crf
        self.video_segment_rejects = video_segment_rejects
        self._dimensions = dimensions
        self.aspect_ratio = aspect_ratio
        self.cutting_method = cutting_method

    @property
    def duration(self):
        """
        (int): Duration of the music video, calculated from durations of video segments
        """
        sum([segment.duration for segment in self.video_segments])

    @property
    def dimensions(self):
        """
        (int, int): _dimensions if set, or calculated from dimensions of video segments and aspect_ratio
        """
        if self._dimensions:
            return self._dimensions
        else:
            return v_sizing.largest_dimensions_for_aspect_ratio(self.video_segments, self.aspect_ratio)

    @property
    def cut_locations(self):
        """
        (list of float): Locations in the music video where a change between video segments occurs (sec)
        """
        cut_locations = []
        running_duration = 0
        for index, segment in enumerate(self.video_segments):
            if index != len(self.video_segments) - 1:
                cut_locations.append(segment.duration + running_duration)
                running_duration += segment.duration

        return cut_locations

    @property
    def cut_intervals(self):
        """
        (list of float): Intervals between each cut location (sec)
        """
        cut_intervals = []
        for segment in self.video_segments:
            cut_intervals.append(segment.duration)

        return cut_intervals

    def compose(self):
        """
        Returns (VideoClip): A composed VideoClip of the music video
        """
        # resize copy of videoSegments (resizing is destructive)
        # concatenate_videoclips
        # Return VideoClip

    def write_to_video_file(self, filename, *args, **kwargs):
        # compose
        # write_videofile()
        # add_auxiliary_tracks

    def write_to_spec_file(self, filename):

    def save_video_segments(self, directory=c.SEGMENTS_PATH_BASE):

    def save_video_segment_rejects(self, directory=c.RS_PATH_BASE):

    def to_spec(self):

    @classmethod
    def from_spec(cls, spec):

