import glob as globber
import os
import random
from typing import Union, List, Optional as Opt, NamedTuple, Tuple

from numpy.random import choice

import mugen.utility as util
from mugen import paths
from mugen.constants import TIME_FORMAT
from mugen.utility import convert_time_to_seconds
from mugen.video.segments.VideoSegment import VideoSegment
from mugen.video.sources.Source import Source, SourceList


class TimeRangeBase(NamedTuple):
    start: float
    end: float


class TimeRange(TimeRangeBase):
    __slots__ = ()

    @convert_time_to_seconds(['start', 'end'])
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

    def __init__(self, file: str, *, time_boundaries: Opt[List[Tuple[(TIME_FORMAT, TIME_FORMAT)]]] = None,
                 **kwargs):
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
        return f"<{self.__class__.__name__}: {self.name}, duration: {self.segment.duration_time_code}, " \
               f"weight: {self.weight}>"

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
            time_ranges = [time_range for time_range in time_ranges if time_range.duration >= duration]
            total_duration = sum([time_range.duration for time_range in time_ranges])
            time_range_weights = [time_range.duration / total_duration for time_range in time_ranges]
            time_range_to_sample = time_ranges[choice(len(time_ranges), p=time_range_weights)]
        else:
            time_range_to_sample = TimeRange(0, self.segment.duration)

        start_time = random.uniform(time_range_to_sample.start, time_range_to_sample.end - duration)
        sampled_clip = self.segment.subclip(start_time, start_time + duration)

        return sampled_clip


class VideoSourceList(SourceList):
    """
    A list of VideoSources
    """
    name: Opt[str]

    def __init__(self, sources=Opt[Union[List[Union[Source, 'VideoSourceList']], str]], **kwargs):
        """
        Parameters
        ----------
        sources
            A list of sources.
            Accepts arbitrarily nested video files, file globs, directories, VideoSources, and VideoSourceLists.
        """
        self.name = None

        if isinstance(sources, str):
            self.name = paths.filename_from_path(sources)

            # Build list of sources from directory or file glob
            if os.path.isdir(sources):
                sources = self._sources_from_files(util.files_from_directory(sources))
            else:
                sources = self._sources_from_files(globber.glob(sources))
        else:
            # Convert any source files to VideoSources, and any lists, file globs or directories to VideoSourceLists
            sources = self._fill_in_sources(sources)

        super().__init__(sources, **kwargs)

    def list_repr(self):
        """
        Repr for use in lists
        """
        if self.name:
            return f"<{self.__class__.__name__} ({len(self)}): {self.name}, weight: {self.weight}>"

        return super().list_repr()

    @staticmethod
    def _sources_from_files(files: List[str]):
        sources = []

        for file in files:
            try:
                source = VideoSource(file)
            except IOError:
                continue

            sources.append(source)

        return sources

    @staticmethod
    def _fill_in_sources(sources: list):
        for index, source in enumerate(sources):
            if isinstance(source, str):
                try:
                    sources[index] = VideoSource(source)
                except IOError:
                    sources[index] = VideoSourceList(source)
            if isinstance(source, list) and not isinstance(source, VideoSourceList):
                sources[index] = VideoSourceList(source)

        return sources
