from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader

from mugen import paths
from mugen import utilities
from mugen.constants import TIME_FORMAT
from mugen.utilities import convert_time_to_seconds
from mugen.video.segments.Segment import Segment


class VideoSegment(Segment, VideoFileClip):
    """
    A segment with video

    Attributes
    ----------
    source_start_time
        Start time of the video segment in the video file (seconds)
    """
    source_start_time: float

    def __init__(self, file: str = None, **kwargs):
        """
        Parameters
        ----------
        file
            path to the video file.
            Supports any extension supported by ffmpeg, in addition to gifs.
        """
        super().__init__(file, **kwargs)

        self.source_start_time = 0
        if not self.fps:
            self.fps = Segment.DEFAULT_VIDEO_FPS

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}, source_start_time: {self.source_start_time_time_code}, " \
               f"duration: {self.duration}>"

    def __getstate__(self):
        """
        Custom pickling
        """
        state = self.__dict__.copy()

        # Remove the video segment's audio and reader to allow pickling
        state['reader'] = None
        state['audio'] = None

        return state

    def __setstate__(self, newstate):
        """
        Custom unpickling
        """
        # Recreate the video segment's audio and reader
        newstate['reader'] = FFMPEG_VideoReader(newstate['filename'])
        newstate['audio'] = AudioFileClip(newstate['filename']).subclip(newstate['source_start_time'],
                                                                        newstate['source_start_time'] +
                                                                        newstate['duration'])
        self.__dict__.update(newstate)

    """ PROPERTIES """

    @property
    def file(self) -> str:
        return self.filename

    @property
    def name(self) -> str:
        return paths.filename_from_path(self.file)

    @property
    def source_end_time(self) -> float:
        return self.source_start_time + self.duration

    @property
    def source_start_time_time_code(self) -> str:
        return utilities.seconds_to_time_code(self.source_start_time)

    """ METHODS """

    @convert_time_to_seconds(['start_time', 'end_time'])
    def subclip(self, start_time: TIME_FORMAT = 0, end_time: TIME_FORMAT = None) -> 'VideoSegment':
        """
        Parameters
        ----------
        start_time
            Start time of the video segment in the source video file

        end_time
            End time of the video segment in the source video file

        Returns
        -------
        A subclip of the original video segment, starting at 'start_time' and ending at 'end_time'
        """
        subclip = super().subclip(start_time, end_time)

        if start_time < 0:
            # Set relative to end
            start_time = self.duration + start_time

        subclip.source_start_time += start_time

        return subclip

    def trailing_buffer(self, duration) -> 'VideoSegment':
        return VideoSegment(self.file).subclip(self.source_end_time, self.source_end_time + duration)

    def overlaps_segment(self, segment: 'VideoSegment') -> bool:
        if not self.file == segment.file:
            return False

        return utilities.ranges_overlap(self.source_start_time, self.source_end_time, segment.source_start_time,
                                   segment.source_end_time)
