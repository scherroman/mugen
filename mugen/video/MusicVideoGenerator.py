import copy
from typing import Any, List, Optional, Union

from tqdm import tqdm

from mugen.audio.Audio import Audio
from mugen.audio.utilities import create_marked_audio_file, mark_audio_file
from mugen.constants import TIME_FORMAT
from mugen.events.EventList import EventList
from mugen.exceptions import MugenError, ParameterError
from mugen.mixins.Filterable import ContextFilter, Filter
from mugen.utilities.conversion import convert_time_to_seconds
from mugen.utilities.system import use_temporary_file_fallback
from mugen.video.filters import DEFAULT_VIDEO_FILTERS, VideoFilter
from mugen.video.MusicVideo import MusicVideo
from mugen.video.segments.ColorSegment import ColorSegment
from mugen.video.segments.VideoSegment import VideoSegment
from mugen.video.sources.SourceSampler import SourceSampler
from mugen.video.sources.VideoSource import VideoSource, VideoSourceList


class MusicVideoGenerator:
    """
    Attributes
    ----------
    audio
        Audio to use for the music video

    video_sources
        source videos to use for generating the music video

    video_filters
        Video filters that each segment in the music video must pass.
        See :class:`~mugen.video.video_filters.VideoFilter` for a list of supported values.
        Defaults to :data:`~mugen.video.video_filters.VIDEO_FILTERS_DEFAULT`

    exclude_video_filters
        Video filters to exclude from default video_filters.
        Takes precedence over video_filters

    include_video_filters
        Video filters to use in addition to default video_filters.
        Takes precedence over exclude_video_filters

    custom_video_filters ~
        Custom video filters to use in addition to video_filters.
        Allows functions wrapped by :class:`~mugen.mixins.Filterable.Filter` or
        :class:`~mugen.mixins.Filterable.ContextFilter`
    """

    audio: Audio
    _duration: float
    video_sources: List[Union[VideoSource, List[VideoSourceList]]]
    video_filters: List[Filter]
    _video_filters: Optional[List[str]]
    exclude_video_filters: Optional[List[str]]
    include_video_filters: Optional[List[str]]
    custom_video_filters: Optional[List[Filter]]

    @convert_time_to_seconds(["duration"])
    def __init__(
        self,
        audio_file: Optional[str] = None,
        video_sources: Optional[
            Union[VideoSourceList, List[Union[VideoSource, str, List[Any]]]]
        ] = None,
        *,
        duration: TIME_FORMAT = None,
    ):
        """
        Parameters
        ----------
        audio_file
            audio file to use for the music video

        video_sources
            Source videos to use for the music video.
            Accepts arbitrarily nested video files, directories, VideoSources, and VideoSourceLists.

        duration
            Duration for the music video if no audio_file is provided
        """
        if not audio_file and not duration:
            raise ParameterError(
                "Must provide either the audio file or duration for the music video."
            )

        self.audio = Audio(audio_file) if audio_file else None
        self._duration = duration

        if video_sources:
            self.video_sources = VideoSourceList(video_sources)

        self._video_filters = None
        self.exclude_video_filters = None
        self.include_video_filters = None
        self.custom_video_filters = None

    @property
    def video_filters(self):
        compiled_video_filters = []

        # Only use default video filters if video_filters is specifically None to allow specifying no filters with an empty array
        video_filter_names = (
            copy.copy(self._video_filters)
            if self._video_filters is not None
            else DEFAULT_VIDEO_FILTERS
        )
        exclude_video_filters = self.exclude_video_filters or []
        include_video_filters = self.include_video_filters or []
        custom_video_filters = self.custom_video_filters or []

        for video_filter in exclude_video_filters:
            try:
                video_filter_names.remove(video_filter)
            except ValueError:
                raise ValueError(f"Unknown video filter {video_filter}")
        video_filter_names.extend(include_video_filters)

        compiled_video_filters = self.collect_video_filters(video_filter_names)
        compiled_video_filters.extend(custom_video_filters)

        return compiled_video_filters

    @video_filters.setter
    def video_filters(self, value: EventList):
        self._video_filters = value

    @staticmethod
    def collect_video_filters(video_filter_names):
        video_filters = []
        for video_filter_name in video_filter_names:
            try:
                video_filters.append(VideoFilter[video_filter_name].value)
            except KeyError as error:
                raise MugenError(
                    f"Unknown video filter '{video_filter_name}'"
                ) from error

        return video_filters

    @property
    def duration(self):
        return self.audio.duration if self.audio else self._duration

    def generate_from_events(
        self, events: Union[EventList, List[TIME_FORMAT]], show_progress: bool = True
    ) -> MusicVideo:
        """
        Generates a MusicVideo from a list of events

        Parameters
        ----------
        events
            Events corresponding to cuts which occur in the music video.
            Either a list of events or event locations.

        show_progress
            Whether to output progress information to stdout
        """
        if not isinstance(events, EventList):
            events = EventList(events, end=self.duration)

        # Get segment durations from cut locations
        segment_durations = events.segment_durations

        (
            music_video_segments,
            rejected_video_segments,
        ) = self._generate_music_video_segments(
            segment_durations, show_progress=show_progress
        )

        # Assemble music video from music video segments and audio
        music_video = MusicVideo(
            music_video_segments, self.audio.file if self.audio else None
        )
        music_video.events = events
        music_video.rejected_segments = rejected_video_segments

        return music_video

    def _generate_music_video_segments(
        self, durations: List[float], *, show_progress: bool = True
    ) -> List[VideoSegment]:
        """
        Generates a list of sampled video segments which pass all trait filters

        Parameters
        ----------
        durations
            durations for each sampled video segment

        show_progress
            Whether to output progress information to stdout

        Returns
        -------
        Sampled video segments
        """
        video_segments = []
        rejected_video_segments = []
        source_sampler = SourceSampler(self.video_sources)
        video_filters = copy.deepcopy(self.video_filters)

        # Set memory for all ContextFilters
        for video_filter in video_filters:
            if isinstance(video_filter, ContextFilter) and video_filter.memory is None:
                video_filter.memory = video_segments

        for duration in tqdm(durations, disable=not show_progress):
            (
                next_video_segment,
                next_rejected_video_segments,
            ) = source_sampler.sample_with_filters(duration, video_filters)
            video_segments.append(next_video_segment)
            rejected_video_segments.extend(next_rejected_video_segments)

        return video_segments, rejected_video_segments

    @use_temporary_file_fallback("output_path", ".mkv")
    def preview_from_events(self, events: Union[EventList, List[TIME_FORMAT]]):
        """
        Creates a new audio file with audible bleeps at event locations

        Parameters
        ----------
        events
            Events to mark in the audio file.

        output_path
            Path to save the output .wav or .mkv file

        show_progress
            Whether to output progress information to stdout
        """
        if not isinstance(events, EventList):
            events = EventList(events, end=self.duration)

        marked_audio_file = self.get_marked_audio(events)

        composite_segments = []
        for index, duration in enumerate(events.segment_durations):
            # Alternate between black & white segments
            color = "black" if index % 2 == 0 else "white"
            composite_segments.append(ColorSegment(color, duration, size=(600, 300)))

        preview = MusicVideo(composite_segments, marked_audio_file)
        preview.events = events
        preview.writer.preset = "ultrafast"

        return preview

    def get_marked_audio(self, events: EventList):
        marked_audio_file = None
        if self.audio.file:
            marked_audio_file = mark_audio_file(self.audio.file, events.locations)
        else:
            marked_audio_file = create_marked_audio_file(
                events.locations,
                self.duration,
            )

        return marked_audio_file
