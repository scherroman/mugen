import glob as globber
import os
import random
import re
from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple, Union

from numpy.random import choice

from mugen.constants import TIME_FORMAT
from mugen.exceptions import ParameterError
from mugen.utilities import system
from mugen.utilities.conversion import convert_time_to_seconds
from mugen.video.segments.VideoSegment import VideoSegment
from mugen.video.sources.Source import Source, SourceList

GLOB_STAR = "*"


class TimeRangeBase(NamedTuple):
    start: float
    end: float


class TimeRange(TimeRangeBase):
    __slots__ = ()

    @convert_time_to_seconds(["start", "end"])
    def __new__(cls, start, end):
        self = super().__new__(cls, start, end)
        return self

    @property
    def duration(self):
        return self.end - self.start


class VideoSource(Source):
    """
    A video source for sampling video segments
    """

    time_boundaries: List[Tuple[(TIME_FORMAT, TIME_FORMAT)]]

    def __init__(
        self,
        file: str,
        *,
        time_boundaries: Optional[List[Tuple[(TIME_FORMAT, TIME_FORMAT)]]] = None,
        **kwargs,
    ):
        """
        Parameters
        ----------
        file
            video file to sample from

        time_boundaries
            the set of time ranges to sample from in the video.
            For supported formats, see :data:`~mugen.constants.TIME_FORMAT`.
        """
        super().__init__(**kwargs)
        self.segment = VideoSegment(file)
        self.time_boundaries = time_boundaries if time_boundaries else []

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}: {self.name}, duration: {self.segment.duration_time_code}, "
            f"weight: {self.weight}>"
        )

    @property
    def file(self):
        return self.segment.file

    @property
    def name(self):
        return self.segment.name

    def sample(self, duration: float) -> VideoSegment:
        """
        Randomly samples a video segment with the specified duration.

        Parameters
        ----------
        duration
            duration of the video segment to sample
        """
        if self.time_boundaries:
            # Select a random time boundary to sample from, weighted by duration
            time_ranges = [TimeRange(*boundary) for boundary in self.time_boundaries]
            time_ranges = [
                time_range
                for time_range in time_ranges
                if time_range.duration >= duration
            ]
            total_duration = sum([time_range.duration for time_range in time_ranges])
            time_range_weights = [
                time_range.duration / total_duration for time_range in time_ranges
            ]
            time_range_to_sample = time_ranges[
                choice(len(time_ranges), p=time_range_weights)
            ]
        else:
            time_range_to_sample = TimeRange(0, self.segment.duration)

        start_time = random.uniform(
            time_range_to_sample.start, time_range_to_sample.end - duration
        )
        sampled_clip = self.segment.subclip(start_time, start_time + duration)

        return sampled_clip


class VideoSourceList(SourceList):
    """
    A list of video sources
    """

    name: Optional[str]

    def __init__(
        self,
        sources=Optional[Union[List[Union[str, Source, "VideoSourceList"]], str]],
        **kwargs,
    ):
        """
        Parameters
        ----------
        sources
            A list of sources.
            Accepts arbitrarily nested video files, directories, globs, Sources, VideoSources, and VideoSourceLists.
        """
        self.name = None
        video_sources = []

        if isinstance(sources, str):
            self.name = Path(sources).stem
            video_sources = self._get_sources_from_path(sources)
        else:
            video_sources = self._get_sources_from_list(sources)

        super().__init__(video_sources, **kwargs)

    def list_repr(self):
        """
        Repr for use in lists
        """
        if self.name:
            return f"<{self.__class__.__name__} ({len(self)}): {self.name}, weight: {self.weight}>"

        return super().list_repr()

    @staticmethod
    def _get_sources_from_path(
        path: str,
    ) -> List[Union[VideoSource, "VideoSourceList"]]:
        sources = []

        if GLOB_STAR in path:
            sources = VideoSourceList._get_sources_from_glob_path(path)
        elif os.path.isdir(path):
            sources = VideoSourceList._get_sources_from_directory(path)
        else:
            sources = [VideoSource(path)]

        if len(sources) == 0:
            raise IOError(f"No file(s) found for {path}")

        return sources

    @staticmethod
    def _get_sources_from_glob_path(
        glob_path: str,
    ) -> List[Union[VideoSource, "VideoSourceList"]]:
        sources = []
        # Escape square brackets, which are common in file names and affect glob
        paths = globber.glob(re.sub(r"([\[\]])", "[\\1]", glob_path))
        for path in paths:
            path_sources = VideoSourceList._get_sources_from_path(path)
            if os.path.isdir(path):
                sources.append(VideoSourceList(path_sources))
            else:
                sources.extend(path_sources)

        return sources

    @staticmethod
    def _get_sources_from_directory(
        directory: str,
    ) -> List[Union[VideoSource, "VideoSourceList"]]:
        sources = []
        for file in system.list_directory_files(directory):
            try:
                sources.append(VideoSource(file))
            except IOError:
                continue

        return sources

    @staticmethod
    def _get_sources_from_list(
        sources_list: List[Union[str, Source, "VideoSourceList"]],
    ) -> List[Union[Source, "VideoSourceList"]]:
        sources = []
        for source in sources_list:
            if isinstance(source, str) and os.path.isfile(source):
                sources.extend(VideoSourceList._get_sources_from_path(source))
            elif isinstance(source, str):
                sources.append(
                    VideoSourceList(VideoSourceList._get_sources_from_path(source))
                )
            elif isinstance(source, Source) or isinstance(source, VideoSourceList):
                sources.append(source)
            elif isinstance(source, list):
                sources.append(VideoSourceList(source))
            else:
                raise ParameterError(f"Unknown source type {source}")

        return sources
