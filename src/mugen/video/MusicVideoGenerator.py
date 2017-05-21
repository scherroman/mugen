from typing import Tuple, Optional as Opt, List, Union

from tqdm import tqdm

import mugen.audio.analysis as librosa
import mugen.video.video_filters as vf
import mugen.location_utility as loc_util
import mugen.video.events as v_events
from mugen.utility import convert_time_list_to_seconds
from mugen.audio import events as a_events
from mugen.mixins.Filterable import Filter, ContextFilter
from mugen.events import Event, EventList
from mugen.audio.events import AudioEventsMode
from mugen.video.events import VideoEventType, VideoEventsMode
from mugen.video.MusicVideo import MusicVideo
from mugen.video.VideoSegment import VideoSegment, VideoSegmentList
from mugen.video.VideoSegmentSampler import VideoSegmentSampler
from mugen.constants import TIME_FORMAT
from mugen.exceptions import ParameterError, MugenError


class MusicVideoGenerator:
    """
    Attributes
    ----------
    audio_file 
        audio file to use for the music video
        
    video_sources 
        source videos to use for the music video
        
    video_filters 
        Video filters that each segment in the music video must pass. 
        See :class:`~mugen.video.video_filters.VideoFilter` for a list of supported values.
        Defaults to :data:`~mugen.video.video_filters.VIDEO_FILTERS_DEFAULT`
        
    custom_video_filters
        Custom video filters to use in addition to video_filters.
        Allows functions wrapped by :class:`~mugen.mixins.Filterable.Filter` or 
        :class:`~mugen.mixins.Filterable.ContextFilter`
    """
    audio_file: str
    video_sources: VideoSegmentList
    video_filters: List[str]
    custom_video_filters: List[Filter]

    def __init__(self, audio_file: str, video_source_files: Opt[List[Union[str, List[str]]]] = None, *,
                 video_sources: Opt[List[Union[VideoSegment, List[VideoSegment]]]] = None,
                 video_source_weights: Opt[List[float]] = None, video_filters: Opt[List[str]] = None,
                 exclude_video_filters: Opt[List[str]] = None, include_video_filters: Opt[List[str]] = None,
                 custom_video_filters: Opt[List[Filter]] = None):
        """
        Parameters
        ----------
        audio_file ~
        
        video_source_files 
            Source video files to use for the music video.
            Accepts both video files and lists of video files
            
        video_sources
            Source VideoSegments to use for the music video.
            Accepts both VideoSegments and lists of VideoSegments
        
        video_source_weights 
            Weights for each source video
            
        video_filters ~
        
        exclude_video_filters 
            Video filters to exclude from default video_filters. 
            Takes precedence over video_filters
            
        include_video_filters 
            Video filters to use in addition to default video_filters. 
            Takes precedence over exclude_video_filters
            
        custom_video_filters ~
        """
        if video_source_files is None and video_sources is None:
            raise ParameterError("Either 'source_video_files' or 'source_videos' must be provided.")

        self.audio_file = audio_file

        if video_sources is not None:
            video_sources = video_sources
        elif video_source_files is not None:
            video_sources = VideoSegment.video_segments_from_irregular_source_list(video_source_files)

        self.video_sources = VideoSegmentList(video_sources, video_source_weights)

        # Compile list of video filters
        self.video_filters = video_filters if video_filters is not None else vf.VIDEO_FILTERS_DEFAULT
        if exclude_video_filters:
            for video_filter in exclude_video_filters:
                self.video_filters.remove(video_filter)
        if include_video_filters:
            self.video_filters.extend(include_video_filters)
        self.custom_video_filters = custom_video_filters or []

    def generate_from_events(self, events: EventList, *, event_modifiers: Opt[dict] = None) -> MusicVideo:
        """
        Generates a MusicVideo from a list of events
        
        Parameters
        ----------
        events
            Events which occur in the music video
            
        event_modifiers
            Modifiers to apply to events. 
            See :class:`~mugen.events.EventsModifer` for available parameters
        """
        events.modify(event_modifiers)

        # Add END event if missing
        if events[-1].type != VideoEventType.END:
            duration = librosa.get_audio_duration(self.audio_file)
            events.append(Event(duration, type=VideoEventType.END))

        cut_locations = [event.location for event in events if
                         event.type == VideoEventType.CUT or
                         event.type == VideoEventType.END]
        cut_intervals = loc_util.intervals_from_locations(cut_locations)

        # Generate music video segments from cut locations
        video_filters = []
        for filter in self.video_filters:
            try:
                video_filters.append(vf.VideoFilter[filter].value)
            except KeyError as e:
                raise MugenError(f"Unknown video filter '{filter}'") from e

        video_filters.extend(self.custom_video_filters)
        video_segment_sampler = VideoSegmentSampler(self.video_sources)
        music_video_segments, rejected_music_video_segments = self._generate_video_segments(video_segment_sampler,
                                                                                            cut_intervals,
                                                                                            video_filters)
        music_video_segments = VideoSegmentList(music_video_segments)
        rejected_music_video_segments = VideoSegmentList(rejected_music_video_segments)

        # Assemble music video from music video segments and audio
        music_video = MusicVideo(self.audio_file, music_video_segments, source_videos=self.video_sources,
                                 rejected_video_segments=rejected_music_video_segments,
                                 video_filters=video_filters)

        return music_video

    @convert_time_list_to_seconds('event_locations')
    def generate_from_event_locations(self, event_locations: List[TIME_FORMAT],
                                      video_events_mode: Opt[VideoEventsMode] = None, *,
                                      event_modifiers: Opt[dict] = None) -> MusicVideo:
        """
        Generates a MusicVideo from a list of event locations

        Parameters
        ----------
        event_locations 
            Timestamps at which an event occurs in the music video
            
        video_events_mode 
            Method of generating video events for event locations.
            See :class:`~mugen.constants.VideoEventType` for supported values. 
            Defaults to 'cut'
            
        event_modifiers 
            Modifiers to apply to generated events. 
            See :class:`~mugen.events.EventsModifer` for available parameters
        """
        if video_events_mode is None:
            video_events_mode = VideoEventsMode.CUTS

        video_event_type = v_events.event_type_for_mode(video_events_mode)
        events = EventList.from_locations(event_locations, type=video_event_type)

        return self.generate_from_events(events, event_modifiers=event_modifiers)

    def generate_from_audio_events(self, audio_events_mode: str,
                                   video_events_mode: Opt[str] = None, *,
                                   event_modifiers: Opt[dict] = None) -> MusicVideo:
        """
        Generates a MusicVideo from event locations in the audio

        Parameters
        ----------
        audio_events_mode 
            Method of generating events from the audio file.
            See :class:`~mugen.audio.constants.AudioEventsMode` for supported values
            Defaults to `beats_untrimmed`
            
        video_events_mode 
            Method of generating video events from audio events.
            See :class:`~mugen.constants.VideoEventsMode` for supported values.
            Defaults to `cuts`
            
        event_modifiers 
            Modifiers to apply to generated events. 
            See :class:`~mugen.events.EventsModifer` for available parameters
        """
        if audio_events_mode is None:
            audio_events_mode = AudioEventsMode.BEATS_UNTRIMMED
        if video_events_mode is None:
            video_events_mode = VideoEventsMode.CUTS

        events = a_events.generate_events_from_audio(self.audio_file, event_mode=audio_events_mode)

        # Convert to video events
        for event in events:
            if video_events_mode == VideoEventsMode.CUTS:
                event.type = VideoEventType.CUT

        return self.generate_from_events(events, event_modifiers=event_modifiers)

    @staticmethod
    def _generate_video_segments(video_segment_sampler: VideoSegmentSampler, durations: List[float],
                                 video_filters: List[Filter]) -> Tuple[List[VideoSegment], List[VideoSegment]]:
        """
        Generates a set of randomly sampled video segments which pass all trait filters

        Parameters
        ----------
        video_segment_sampler 
            source to randomly sample video segments from
            
        durations 
            durations for each sampled video segment
            
        video_filters 
            filters to apply to each sampled video segment
            
        Returns
        -------
        Tuple of video segments and rejected video segments
        """
        video_segments = []
        rejected_video_segments = []

        # Set memory for all ContextFilters
        for video_filter in video_filters:
            if type(video_filter) == ContextFilter and video_filter.memory is None:
                video_filter.memory = video_segments

        for duration in tqdm(durations):
            video_segment = None

            while not video_segment:
                video_segment = video_segment_sampler.sample(duration)

                video_segment.passed_filters, video_segment.failed_filters = video_segment.apply_filters(video_filters)
                if not video_segment.failed_filters:
                    video_segments.append(video_segment)
                else:
                    rejected_video_segments.append(video_segment)
                    video_segment = None

        # Clear memory for all ContextFilters
        for video_filter in video_filters:
            if type(video_filter) == ContextFilter:
                video_filter.memory = []

        return video_segments, rejected_video_segments

    def regenerate(self, spec_file: str) -> MusicVideo:
        """
        Regenerates a MusicVideo from a spec file
        """
        return


def regenerate_video_segments(spec, replace_segments):
    """
    Regenerates the video segments from the videos specified in the spec
    """
    return
    # video_files = [video_file['file_path'] for video_file in spec['video_files']]
    # videos = get_videos(video_files)
    # regen_video_segments = []
    #
    # print("Regenerating video segments from {} videos according to spec...".format(len(videos)))
    #
    # # Regenerate video segments from videos
    # for index, video_segment in enumerate(tqdm(spec['video_segments'])):
    #     replace_segment = True if index in replace_segments else False
    #     if replace_segment:
    #         # Wait to replace segments until later
    #         continue
    #
    #     # Regenerate segment from the spec
    #     try:
    #         regen_video_segment = regenerate_video_segment(videos, video_segment, spec['video_files'])
    #     except Exception as e:
    #         print(f"Error regenerating video segment {index}. Will replace with a new one. Error: {e}")
    #         replace_segments.append(index)
    #         continue
    #
    #     regen_video_segments.append(regen_video_segment)
    #
    # # Replace segments as needed and requested
    # # Sort segment indeces beforehand to replace in order
    # replace_segments.sort()
    # for index in replace_segments:
    #     video_segment = spec['video_segments'][index]
    #     # Generate new random segment
    #     replacement_video_segment, rejected_segments = generate_video_segment(videos, video_segment['duration'],
    #                                                                           regen_video_segments)
    #
    #     # Add metadata for music video spec
    #     replacement_video_segment.sequence_number = index
    #     replacement_video_segment.beat_interval_numbers = video_segment['beat_interval_numbers']
    #
    #     regen_video_segments.insert(index, replacement_video_segment)
    #
    # if c.music_video_dimensions:
    #     regen_video_segments = [segment.crop_scale(c.music_video_dimensions) for segment in regen_video_segments]
    #
    # return regen_video_segments


""" HELPER FUNCTIONS """

def regenerate_video_segment(videos, video_segment, video_files):
    """
    Attempts to regenerate a spec file video segment.
    If this cannot be done successfully, returns None
    """
    return
    # video_file = video_files[video_segment['video_number']]
    # video = next(video for video in videos if video.src_video_file == video_file['file_path'])
    # start_time = video_segment['video_start_time']
    # end_time = video_segment['video_end_time']
    # offset = video_file['offset'] if video_file['offset'] else 0
    #
    # regen_video_segment = video.subclip(start_time + offset, end_time + offset)
    # # Add metadata for music video spec
    # regen_video_segment.sequence_number = video_segment['sequence_number']
    # regen_video_segment.beat_interval_numbers = video_segment['beat_interval_numbers']
    #
    # return regen_video_segment