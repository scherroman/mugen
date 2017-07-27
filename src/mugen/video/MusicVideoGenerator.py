import copy
from enum import Enum
from typing import Optional as Opt, List, Union, Any

from moviepy.audio.io.AudioFileClip import AudioFileClip
from tqdm import tqdm

import mugen.audio.utility as a_util
import mugen.video.io.subtitles as v_io
import mugen.video.video_filters as vf
from mugen.audio.Audio import Audio
from mugen.constants import TIME_FORMAT
from mugen.events import EventList
from mugen.exceptions import MugenError
from mugen.mixins.Filterable import Filter, ContextFilter
from mugen.video.MusicVideo import MusicVideo
from mugen.video.io.VideoWriter import VideoWriter
from mugen.video.io.subtitles import SubtitleTrack
from mugen.video.moviepy.CompositeVideoClip import CompositeVideoClip
from mugen.video.segments.ColorSegment import ColorSegment
from mugen.video.segments.VideoSegment import VideoSegment
from mugen.video.sources.SourceSampler import SourceSampler
from mugen.video.sources.VideoSource import VideoSource, VideoSourceList


class PreviewMode(str, Enum):
    """
    audio: Produce an audio preview
    visual: Produce an audio-visual preview
    """
    AUDIO = 'audio'
    VISUAL = 'visual'


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

    meta
        Json serializable dictionary with extra metadata
    """
    audio: Audio
    video_sources: List[Union[VideoSource, List[VideoSourceList]]]
    video_filters: List[Filter]

    meta: dict

    class Meta(str, Enum):
        REJECTED_SEGMENT_STATS = 'rejected_segment_stats'

    def __init__(self, audio_file: str,
                 video_sources: Opt[Union[VideoSourceList, List[Union[VideoSource, str, List[Any]]]]] = None, *,
                 video_filters: Opt[List[str]] = None, exclude_video_filters: Opt[List[str]] = None,
                 include_video_filters: Opt[List[str]] = None, custom_video_filters: Opt[List[Filter]] = None):
        """
        Parameters
        ----------
        audio_file 
            audio file to use for the music video

        video_sources
            Source videos to use for the music video.
            Accepts arbitrarily nested video files, directories, VideoSources, and VideoSourceLists.

        video_filters ~
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
        self.audio = Audio(audio_file)

        if video_sources:
            self.video_sources = VideoSourceList(video_sources)

        # Assemble list of video filter names
        video_filter_names = video_filters if video_filters is not None else vf.VIDEO_FILTERS_DEFAULT
        if exclude_video_filters:
            for video_filter in exclude_video_filters:
                video_filter_names.remove(video_filter)
        if include_video_filters:
            video_filter_names.extend(include_video_filters)
        custom_video_filters = custom_video_filters or []

        # Compile video filters
        self.video_filters = []
        for filter_name in video_filter_names:
            try:
                self.video_filters.append(vf.VideoFilter[filter_name].value)
            except KeyError as e:
                raise MugenError(f"Unknown video filter '{filter}'") from e
        self.video_filters.extend(custom_video_filters)

        self.meta = {self.Meta.REJECTED_SEGMENT_STATS: []}

    def generate_from_video_cuts(self, video_cuts: Union[EventList, List[TIME_FORMAT]]) -> MusicVideo:
        """
        Generates a MusicVideo from a list of video events
        
        Parameters
        ----------
        video_cuts
            Cut events which occur in the music video.
            Either a list of events or event locations.
        """
        if not isinstance(video_cuts, EventList):
            video_cuts = EventList(video_cuts, end=self.audio.duration)

        # Get segment durations from cut locations
        segment_durations = video_cuts.segment_durations

        music_video_segments = self._generate_music_video_segments(segment_durations)

        # Assemble music video from music video segments and audio
        music_video = MusicVideo(music_video_segments, self.audio.audio_file)

        return music_video

    def _generate_music_video_segments(self, durations: List[float]) -> List[VideoSegment]:
        """
        Generates a list of sampled video segments which pass all trait filters

        Parameters
        ----------
        durations 
            durations for each sampled video segment

        Returns
        -------
        Sampled video segments
        """
        video_segments = []
        video_segment_sampler = SourceSampler(self.video_sources)

        # Make deep copies of filters
        video_filters = copy.deepcopy(self.video_filters)

        # Set memory for all ContextFilters
        for video_filter in video_filters:
            if isinstance(video_filter, ContextFilter) and video_filter.memory is None:
                video_filter.memory = video_segments

        for duration in tqdm(durations):
            video_segment = None

            while not video_segment:
                video_segment = video_segment_sampler.sample(duration)

                video_segment.passed_filters, video_segment.failed_filters = \
                    video_segment.apply_filters(video_filters)
                if not video_segment.failed_filters:
                    video_segments.append(video_segment)
                else:
                    self.meta[self.Meta.REJECTED_SEGMENT_STATS].append(video_segment.__dict__)
                    video_segment = None

        return video_segments

    def preview_events(self, events: Union[EventList, List[TIME_FORMAT]], output_path: str,
                       mode: str = PreviewMode.VISUAL, **kwargs):
        """
        Creates a new audio file with audible bleeps at event locations

        Parameters
        ----------
        events
            Events to mark in the audio file.

        output_path
            Path to save the output .wav or .mkv file

        mode
            Method of previewing. Visual by default.
            See :class:`~mugen.audio.Audio.PreviewMode` for supported values.
        """
        if not isinstance(events, EventList):
            events = EventList(events, end=self.audio.duration)

        if mode == PreviewMode.AUDIO:
            a_util.create_marked_audio_file(self.audio.audio_file, events.locations, output_path)
        elif mode == PreviewMode.VISUAL:
            temp_marked_audio_file = a_util.create_marked_audio_file(self.audio.audio_file, events.locations)

            composite_segments = []
            for index, duration in enumerate(events.segment_durations):
                # Alternate black & white
                color = 'black' if index % 2 == 0 else 'white'
                composite_segments.append(ColorSegment(color, duration, size=(600, 300)))

            preview = MusicVideo(composite_segments, temp_marked_audio_file)
            preview.writer.preset = 'ultrafast'

            temp_output_path = preview.write_to_video_file(audio=True, auxiliary_tracks=False, **kwargs)
            self._add_preview_auxiliary_tracks(temp_output_path, events, output_path)

    @staticmethod
    def _add_preview_auxiliary_tracks(video_file: str, events: EventList, output_path: str):
        """
        Adds metadata subtitle tracks to the preview

        Parameters
        ----------
        video_file
            The video file to add tracks to

        events
            Events to create auxiliary tracks from

        output_path
            The final music video output file with added auxiliary tracks
        """
        locations = events.locations
        events_str = [event.index_repr(index) for index, event in enumerate(events)]

        subtitle_track_events = SubtitleTrack.create(events_str, 'events', locations=locations, default=True)

        subtitle_tracks = [subtitle_track_events]
        v_io.add_tracks_to_video(video_file, output_path, subtitle_tracks=subtitle_tracks)

