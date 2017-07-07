import json
import random
from typing import Optional as Opt, List, Tuple, Union, Any

import copy
from moviepy.editor import VideoFileClip
from moviepy.video import VideoClip

import mugen.utility as util
import mugen.video.sizing as v_sizing
import mugen.video.effects as v_effects
from mugen.video.effects import VideoEffect
from mugen import paths
from mugen.utility import convert_time_to_seconds
from mugen.video.sizing import Dimensions
from mugen.constants import TIME_FORMAT
from mugen.video.constants import LIST_3D
from mugen.mixins.Taggable import Taggable
from mugen.mixins.Filterable import Filterable
from mugen.mixins.Weightable import Weightable, WeightableList

DEFAULT_VIDEO_FPS = 24


class VideoSegment(Taggable, Weightable, Filterable, VideoFileClip):
    """
    A segment of video from a video file

    Attributes
    ----------
    source_start_time
        Start time of the video segment in the video file (seconds)

    effects
        A list of effects to apply to the video when composed
    """
    source_start_time: float
    effects: List[VideoEffect]

    def __init__(self, filename: str, *, audio: bool = True, **kwargs):
        """
        Parameters
        ----------
        filename
            The name of the video file.
            Supports any extension supported by ffmpeg
            
        audio
            Enables or disables audio
        """
        super().__init__(**kwargs)
        VideoFileClip.__init__(self, filename, audio=audio, **kwargs)

        self.source_start_time = 0
        self.effects = []

        # Parent VideFileClip will not always be able to properly read an fps value
        if not self.fps:
            self.fps = DEFAULT_VIDEO_FPS

    def __repr__(self):
        filename = paths.filename_from_path(self.video_file)
        return f"<{self.__class__.__name__}, file: {filename}, source_start_time:{self.source_start_time}, " \
               f"duration: {self.duration}>"

    """ PROPERTIES """

    @property
    def video_file(self):
        return self.filename

    @property
    def source_end_time(self):
        return self.source_start_time + self.duration

    @property
    def duration_time_code(self):
        return util.seconds_to_time_code(self.duration)

    @property
    def dimensions(self) -> Dimensions:
        return Dimensions(self.w, self.h)

    @property
    def aspect_ratio(self) -> float:
        return self.w / self.h

    @property
    def resolution(self) -> int:
        return self.w * self.h

    @property
    def first_frame(self) -> LIST_3D:
        return self.get_frame(t=0)

    @property
    def middle_frame(self) -> LIST_3D:
        return self.get_frame(t=self.duration / 2)

    @property
    def last_frame(self) -> LIST_3D:
        return self.get_frame(t=self.duration)

    @property
    def first_last_frames(self) -> List[LIST_3D]:
        return [self.first_frame, self.last_frame]

    @property
    def first_middle_last_frames(self) -> List[LIST_3D]:
        return [self.first_frame, self.middle_frame, self.last_frame]

    """ EFFECTS """

    def add_crossfade(self, duration: float = v_effects.FADE_DURATION):
        """
        Adds a crossfade effect to the beginning of the video segment.
        This effect will only be applied when composed inside a music video
        """
        self.effects.append(v_effects.CrossFade(duration))

    def add_fadein(self, duration: float = v_effects.FADE_DURATION, color: str = v_effects.FADE_COLOR):
        """
        Adds a fade-in effect to the video segment.
        """
        self.effects.append(v_effects.FadeIn(duration, color))

    def add_fadeout(self, duration: float = v_effects.FADE_DURATION, color: str = v_effects.FADE_COLOR):
        """
        Adds a fade-out effect to the video segment.
        """
        self.effects.append(v_effects.FadeOut(duration, color))

    """ METHODS """

    def copy(self) -> 'VideoSegment':
        new_segment = super().copy()

        # Deepcopy effects
        new_segment.effects = copy.deepcopy(self.effects)

        return new_segment

    def compose(self) -> 'VideoSegment':
        """
        Composes the video segment, applying all effects

        Returns
        -------
        A new video segment with all effects applied
        """
        segment = self

        for effect in self.effects:
            if isinstance(effect, v_effects.FadeIn):
                segment = segment.fadein(effect.duration, effect.rgb_color)
                segment.audio = segment.audio.audio_fadein(effect.duration)
            elif isinstance(effect, v_effects.FadeOut):
                segment = segment.fadeout(effect.duration, effect.rgb_color)
                segment.audio = segment.audio.audio_fadeout(effect.duration)

        return segment

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
        A subclip of the original video file, starting at 'start_time' and ending at 'end_time'
        """
        subclip = super().subclip(start_time, end_time)

        if start_time < 0:
            # Set relative to end
            start_time = self.duration + start_time

        subclip.source_start_time += start_time

        return subclip

    @convert_time_to_seconds(['duration'])
    def random_subclip(self, duration: TIME_FORMAT) -> 'VideoSegment':
        start_time = random.uniform(0, self.duration - duration)

        return self.subclip(start_time, start_time + duration)

    def crop_scale(self, desired_dimensions: Tuple[int, int]) -> 'VideoSegment':
        """
        Returns
        -------
        A new VideoSegment, cropped and/or scaled as necessary to reach desired dimensions
        """
        desired_dimensions = Dimensions(*desired_dimensions)
        segment = self

        if segment.aspect_ratio != desired_dimensions.aspect_ratio:
            # Crop video to match desired aspect ratio
            x1, y1, x2, y2 = v_sizing.crop_coordinates_for_aspect_ratio(segment.dimensions,
                                                                        desired_dimensions.aspect_ratio)
            segment = segment.crop(x1=x1, y1=y1, x2=x2, y2=y2)

        if segment.dimensions != desired_dimensions:
            # Resize video to match aspect ratio
            segment = segment.resize(desired_dimensions)

        return segment

    def overlaps_segment(self, segment: 'VideoSegment') -> bool:
        if not self.filename == segment.filename:
            return False

        return util.ranges_overlap(self.source_start_time, self.source_end_time, segment.source_start_time,
                                   segment.source_end_time)

    def to_spec(self) -> str:
        spec = {'source_video': self.filename,
                'source_start_time': self.source_start_time,
                'duration': self.duration}

        return json.dumps(spec)

    @classmethod
    def from_spec(cls, spec: dict) -> 'VideoSegment':
        video_segment = cls(spec['source_video'])
        video_segment = video_segment.subclip(spec['source_start_time'], spec['duration'])

        return video_segment

    @staticmethod
    def video_segments_from_irregular_source_list(video_sources: List[Union[str, List[str]]]) -> List['VideoSegment']:
        """
        Converts an arbitrarily nested irregular list of video sources to VideoSegments
        """
        video_segments = []

        for video_source in video_sources:
            if type(video_source) is list:
                video_segments.append(VideoSegment.video_segments_from_irregular_source_list(video_source))
            else:
                video_segments.append(VideoSegment(video_source))

        return video_segments

    def ipython_display(self, *args, **kwargs):
        """
        Fixes inheritance bug with moviepy's ipython_display
        """
        seg_copy = self.copy()
        seg_copy.__class__ = VideoFileClip
        return seg_copy.ipython_display(*args, **kwargs)


class VideoSegmentList(WeightableList):
    """
    A list of Video Segments with extended functionality
    """

    def __init__(self, video_segments: Opt[List[Union[VideoSegment, List[Any]]]] = None,
                 weights: Opt[List[float]] = None):
        """
        Parameters
        ----------
        video_segments
            An arbitrarily nested irregular list of VideoSegments and lists of VideoSegments.
            VideoSegments will be flattened.
            e.g. [S1, S2, [S3, S4]] -> [S1, S2, S3, S4]

        weights
            Weights to distribute across the video_segments
        """
        if video_segments is None:
            video_segments = []

        super().__init__(video_segments, weights)

    def to_spec(self) -> List[dict]:
        spec = [segment.to_spec() for segment in self]

        return json.dumps(spec)
