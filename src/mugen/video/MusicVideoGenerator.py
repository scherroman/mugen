from typing import Tuple, Optional as Opt, List

import mugen.utility as util
import mugen.audio.librosa as librosa
import mugen.video.video_filters as vf
from mugen.mixins.Filterable import Filter, ContextFilter
from mugen.video.MusicVideo import MusicVideo
from mugen.video.VideoSegment import VideoSegment
from mugen.video.VideoSegmentSampler import VideoSegmentSampler
from mugen.audio.utility import validate_speed_multiplier
from mugen.constants import TIME_FORMAT
from mugen.exceptions import ParameterError


class MusicVideoGenerator:
    """
    Attributes:
        video_filters: names of video filters that each segment in the music video must pass.
        exclude_video_filters: names of video filters to exclude. 
                               Takes precedence over video_filters
        include_video_filters: video filters to use in addition to video_filters. 
                               Takes precedence over exclude_video_filters
                              
    See video_filters for a list of supported and default video filters
    """
    source_videos: List[VideoSegment]

    audio_file: Opt[str] = None
    video_filters: List[str]

    def __init__(self, source_video_files: Opt[List[str]] = None, source_videos: Opt[List[VideoSegment]] = None,
                 audio_file: Opt[str] = None, weights: Opt[List[float]] = None,
                 video_filters: Opt[List[str]] = None, exclude_video_filters: Opt[List[str]] = None,
                 include_video_filters: Opt[List[str]] = None):
        if not source_video_files and not source_videos:
            raise ParameterError("Either 'source_video_files' or 'source_videos' must be provided.")

        if source_videos:
            self.source_videos = source_videos
        elif source_video_files:
            self.source_videos = [VideoSegment(file, not audio_file) for file in source_video_files]
        if weights:
            for source_video, weight in zip(source_videos, weights):
                source_video.weight = weight

        # Compile list of video filters
        self.video_filters = video_filters if video_filters else vf.VIDEO_FILTERS_STANDARD
        if exclude_video_filters:
            for video_filter in exclude_video_filters:
                video_filters.remove(video_filter)
        if include_video_filters:
            video_filters.extend(include_video_filters)

        if audio_file:
            self.audio_file = audio_file

    def generate_from_event_locations(self, event_locations: List[TIME_FORMAT] = None) -> MusicVideo:
        """
        Generates a MusicVideo object from a list of event locations

        Args:
            event_locations: timestamps at which an event occurs in the music video
        """
        event_intervals = util.intervals_from_locations(event_locations)
        video_segment_sampler = VideoSegmentSampler(self.source_videos)

        music_video_segments, rejected_music_video_segments = self._generate_video_segments(video_segment_sampler,
                                                                                            event_intervals,
                                                                                            self.video_filters)

        music_video = MusicVideo(music_video_segments, self.audio_file, source_videos=self.source_videos,
                                 rejected_video_segments=rejected_music_video_segments,
                                 video_segment_filters=self.video_filters)

        return music_video

    def generate_from_cut_locations(self, cut_locations: List[TIME_FORMAT] = None) -> MusicVideo:
        """
        Generates a MusicVideo from a list of cut locations
        
        Args:
            cut_locations: timestamps at which to cut between video segments
        """
        duration = librosa.get_audio_duration(self.audio_file)
        cut_locations.append(duration)

        return self.generate_from_event_locations(cut_locations)

    @validate_speed_multiplier
    def generate_from_audio_events(self, speed_multiplier: Opt[float] = None,
                                   speed_multiplier_offset: Opt[int] = None) -> MusicVideo:
        """
        Generates a MusicVideo from beat locations in the audio
        
        Args:
            speed_multiplier: Speeds up or slows down events by grouping them together or splitting them up.
                              Must be of the form x or 1/x, where x is a natural number.
            speed_multiplier_offset: Offsets the grouping of events for slowdown speed_multipliers. 
                                     Takes a max offset of x - 1 for a slowdown of 1/x, where x is a natural number.
        """
        beat_locations = librosa.get_beat_locations(self.audio_file, trim=False)

        if speed_multiplier:
            beat_locations = util.locations_after_speed_multiplier(beat_locations, speed_multiplier,
                                                                   speed_multiplier_offset)

        return self.generate_from_cut_locations(beat_locations)

    @staticmethod
    def _generate_video_segments(video_segment_sampler: VideoSegmentSampler, durations: List[float],
                                 video_filters: Opt[List[Filter]] = None) -> Tuple[List[VideoSegment],
                                                                                   List[VideoSegment]]:
        """
        Generates a set of randomly sampled video segments which pass all trait filters
        
        Args:
            video_segment_sampler: source to randomly sample video segments from
            durations: durations for each sampled video segment
            video_filters: filters to apply to each sampled video segment

        Returns:

        """
        video_filters = video_filters if video_filters else []
        video_segments = []
        rejected_video_segments = []

        # Set memory for all ContextFilters
        for video_filter in video_filters:
            if type(video_filter) == ContextFilter and video_filter.memory is None:
                video_filter.memory = video_segments

        for duration in durations:
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

    def regenerate(spec_file: str) -> MusicVideo:
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