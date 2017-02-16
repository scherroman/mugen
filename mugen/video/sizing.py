import logging

# Project modules
from mugen.video import utility as v_util
import mugen.settings as s

def resize_video_segments(video_segments):
    """
    Crop and/or resize video segments as necessary
    to reach chosen dimensions of music video
    """
    resized_video_segments = []

    music_video_aspect_ratio = s.music_video_dimensions[0]/float(s.music_video_dimensions[1])

    for video_segment in video_segments:
        resized_video_segment = None
        width = video_segment.size[0]
        height = video_segment.size[1]
        aspect_ratio = width/float(height)

        # Crop video segment if needed, to match aspect ratio of music video dimensions
        if aspect_ratio > music_video_aspect_ratio:
            # Crop sides
            cropped_width = int(music_video_aspect_ratio * height)
            width_difference = width - cropped_width
            video_segment = video_segment.crop(x1 = width_difference/2, x2 = width - width_difference/2)
        elif aspect_ratio < music_video_aspect_ratio:
            # Crop top & bottom
            cropped_height = int(width/music_video_aspect_ratio)
            height_difference = height - cropped_height
            video_segment = video_segment.crop(y1 = height_difference/2, y2 = height - height_difference/2)

        # Resize video if needed, to match music video dimensions
        if tuple(video_segment.size) != s.music_video_dimensions:
            # Video needs resize
            resized_video_segment = video_segment.resize(s.music_video_dimensions)
        else:
            # Video is already correct size
            resized_video_segment = video_segment
            
        resized_video_segments.append(resized_video_segment)

    return resized_video_segments

def calculate_largest_widescreen_dimensions(video_files):
    """
    Returns the largest widescreen (16:9) dimensions possible for a group of videos
    """
    # Get videos
    music_video_dimensions = None
    largest_widescreen_dimensions = None
    videos = v_util.get_videos(video_files)
    logging.debug("\n")

    unique_dimensions = set()

    for video in videos:
        closest_widescreen_dimensions = None
        width = video.size[0]
        height = video.size[1]
        aspect_ratio = width/float(height)
        unique_dimensions.add((width, height))

        logging.debug(video.src_video_file)
        logging.debug("dimensions: {}".format(video.size))

        # Crop sides
        if aspect_ratio > s.WIDESCREEN_ASPECT_RATIO:
            cropped_width = int(s.WIDESCREEN_ASPECT_RATIO * height)
            closest_widescreen_dimensions = (cropped_width, height)
        # Crop top & bottom
        elif aspect_ratio < s.WIDESCREEN_ASPECT_RATIO:
            cropped_height = int(width/s.WIDESCREEN_ASPECT_RATIO)
            closest_widescreen_dimensions = (width, cropped_height)
        else:
            closest_widescreen_dimensions = (width, height)

        logging.debug("closest_widescreen_dimensions: {}\n".format(closest_widescreen_dimensions))

        # Check if the closest_widescreen_dimensions are the largest so far
        if not largest_widescreen_dimensions:
            largest_widescreen_dimensions = closest_widescreen_dimensions
        elif closest_widescreen_dimensions[0] * closest_widescreen_dimensions[1] > \
             largest_widescreen_dimensions[0] * largest_widescreen_dimensions[1]:
            largest_widescreen_dimensions = closest_widescreen_dimensions

    # Only one set of dimensions, use those
    if len(unique_dimensions) == 1:
        music_video_dimensions = next(iter(unique_dimensions))
        print("Using video dimensions: {}".format(music_video_dimensions))
    # Multiple sets of dimensions, use the largest widescreen dimensions calculated
    else:
        music_video_dimensions = largest_widescreen_dimensions
        print("Multiple video sizes detected. Using largest widescreen dimensions possible: {}".format(music_video_dimensions))

    return music_video_dimensions