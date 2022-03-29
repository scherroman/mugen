import os
from pathlib import Path
from typing import List

from mugen import Filter, MusicVideo, MusicVideoGenerator
from mugen.exceptions import ParameterError
from mugen.mixins import Persistable
from mugen.utilities import system
from mugen.video.effects import FadeIn, FadeOut
from mugen.video.io.VideoWriter import VideoWriter
from mugen.video.sources.VideoSource import VideoSourceList
from scripts.cli.events import prepare_events
from scripts.cli.utilities import message, shutdown


def create_music_video(args):
    music_video, generator = generate_music_video(args)
    apply_effects(music_video, args)
    print_rejected_segment_stats(music_video, generator.video_filters)
    output_music_video(music_video, args)


def generate_music_video(args) -> MusicVideo:
    audio_source = args.audio_source
    duration = args.duration
    video_sources = args.video_sources
    video_source_weights = args.video_source_weights
    video_filters = args.video_filters
    exclude_video_filters = args.exclude_video_filters
    include_video_filters = args.include_video_filters

    video_sources = VideoSourceList(video_sources, weights=video_source_weights)
    generator = MusicVideoGenerator(audio_source, video_sources, duration=duration)
    generator.video_filters = video_filters
    generator.exclude_video_filters = exclude_video_filters
    generator.include_video_filters = include_video_filters

    message(
        f"Weights\n------------\n{generator.video_sources.flatten().weight_stats()}"
    )

    try:
        events = prepare_events(generator, args)
    except ParameterError as error:
        shutdown(str(error))

    message("Generating music video from video segments and audio...")

    music_video = generator.generate_from_events(events)

    return music_video, generator


def apply_effects(music_video: MusicVideo, args):
    fade_in = args.fade_in
    fade_out = args.fade_out

    # Apply effects
    if fade_in:
        music_video.segments[0].effects.append(FadeIn(fade_in))
    if fade_out:
        music_video.segments[-1].effects.append(FadeOut(fade_out))


def output_music_video(music_video: MusicVideo, args):
    video_preset = args.video_preset
    video_codec = args.video_codec
    video_crf = args.video_crf
    audio_codec = args.audio_codec
    audio_bitrate = args.audio_bitrate
    use_original_audio = args.use_original_audio
    video_dimensions = args.video_dimensions
    video_aspect_ratio = args.video_aspect_ratio

    (
        music_video_directory,
        music_video_output_path,
        music_video_pickle_path,
    ) = prepare_output_directory(args)

    message(f"Writing music video '{music_video_output_path}'...")

    music_video.writer.preset = video_preset
    music_video.writer.codec = video_codec
    music_video.writer.crf = video_crf
    music_video.writer.audio_codec = audio_codec
    music_video.writer.audio_bitrate = audio_bitrate
    if use_original_audio:
        music_video.audio_file = None
    if video_dimensions:
        music_video.dimensions = video_dimensions
    if video_aspect_ratio:
        music_video.aspect_ratio = video_aspect_ratio

    music_video.write_to_video_file(music_video_output_path)
    music_video.save(music_video_pickle_path)
    output_segments(music_video, music_video_directory, args)


def prepare_output_directory(args):
    output_directory = args.output_directory
    video_name = args.video_name

    # Create the directory for the music video
    music_video_name = get_music_video_name(output_directory, video_name)
    music_video_directory = os.path.join(output_directory, music_video_name)
    music_video_output_path = os.path.join(
        music_video_directory, music_video_name + VideoWriter.DEFAULT_VIDEO_EXTENSION
    )
    music_video_pickle_path = os.path.join(
        music_video_directory, music_video_name + Persistable.PICKLE_EXTENSION
    )
    system.ensure_directory_exists(music_video_directory)

    return music_video_directory, music_video_output_path, music_video_pickle_path


def output_segments(music_video: MusicVideo, directory: str, args):
    save_segments = args.save_segments
    save_rejected_segments = args.save_rejected_segments

    if save_segments:
        message("Saving video segments...")
        music_video.write_video_segments(directory)

    if save_rejected_segments:
        message("Saving rejected video segments...")
        music_video.write_rejected_video_segments(directory)


def preview_music_video(args):
    output_directory = args.output_directory
    audio_source = args.audio_source
    duration = args.duration

    # Prepare Inputs
    preview_name = get_preview_path(
        output_directory, VideoWriter.DEFAULT_VIDEO_EXTENSION
    )
    output_path = os.path.join(output_directory, preview_name)

    generator = MusicVideoGenerator(audio_source, duration=duration)
    try:
        events = prepare_events(generator, args)
    except ParameterError as error:
        shutdown(str(error))

    message(f"Creating preview '{Path(output_path).stem}'...")

    preview = generator.preview_from_events(events)
    preview.write_to_video_file(output_path)


def get_music_video_name(directory: str, basename: str):
    count = 0
    while True:
        music_video_name = basename + f"_{count}"
        music_video_path = os.path.join(directory, music_video_name)

        if not os.path.exists(music_video_path):
            break

        count += 1

    return music_video_name


def get_preview_path(directory: str, extension: str) -> str:
    count = 0
    while True:
        preview_name = f"music_video_preview_{count}{extension}"
        preview_path = os.path.join(directory, preview_name)

        if not os.path.exists(preview_path):
            break

        count += 1

    return preview_name


def print_rejected_segment_stats(music_video: MusicVideo, video_filters: List[Filter]):
    message("Filter results:")
    rejected_segments = music_video.rejected_segments
    for video_filter in video_filters:
        number_of_failing_segments = sum(
            1
            for segment in rejected_segments
            if video_filter.name in segment.failed_filters
        )

        print(
            f"{number_of_failing_segments} segments failed filter {video_filter.name}"
        )
