import os
import random
from typing import Union, List, Optional as Opt

from mugen import paths
from mugen.video.segments.VideoSegment import VideoSegment
from mugen.video.sources.Source import Source, SourceList
import mugen.utility as util


class VideoSource(Source):
    """
    A video source for sampling video segments
    """

    def __init__(self, file: str, **kwargs):
        super().__init__(**kwargs)
        self.segment = VideoSegment(file)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}, duration: {self.duration_time_code}, weight: {self.weight}>"

    @property
    def file(self):
        return self.segment.file

    @property
    def name(self):
        return self.segment.name

    @property
    def duration_time_code(self) -> str:
        return self.segment.duration_time_code

    def sample(self, duration: float) -> VideoSegment:
        """
        Randomly samples a video segment with the specified duration

        Parameters
        ----------
        duration
            duration of the video segment to sample
        """
        start_time = random.uniform(0, self.segment.duration - duration)
        sampled_clip = self.segment.subclip(start_time, start_time + duration)

        return sampled_clip


class VideoSourceList(SourceList):
    """
    A list of VideoSources
    """
    directory: Opt[str]

    def __init__(self, sources=Opt[Union[List[Union[Source, 'VideoSourceList']], str]], **kwargs):
        """
        Parameters
        ----------
        sources
            A list of sources.
            Accepts arbitrarily nested video files, directories, VideoSources, and VideoSourceLists.
        """
        self.directory = None

        if isinstance(sources, str):
            # Build list of sources from directory
            self.directory = sources
            sources = self._sources_from_directory(self.directory)
        else:
            # Convert any source files to VideoSources, and any lists or directories to VideoSourceLists
            sources = self._fill_in_sources(sources)

        super().__init__(sources, **kwargs)

    def list_repr(self):
        """
        Repr for use in lists
        """
        if self.name:
            return f"<{self.__class__.__name__} ({len(self)}): {self.name}, weight: {self.weight}>"

        return super().list_repr()

    @property
    def name(self):
        return paths.filename_from_path(self.directory) if self.directory else None

    @staticmethod
    def _sources_from_directory(directory: str):
        sources = []

        files = util.files_from_directory(directory)
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
                if os.path.isdir(source):
                    sources[index] = VideoSourceList(source)
                else:
                    sources[index] = VideoSource(source)
            if isinstance(source, list) and not isinstance(source, VideoSourceList):
                sources[index] = VideoSourceList(source)

        return sources
