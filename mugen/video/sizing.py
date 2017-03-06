from enum import Enum
import logging

# Project modules
from mugen.video import utility as v_util
import mugen.constants as c

class AspectRatio(float, Enum):
    FULLSCREEN = (4, 3)
    WIDESCREEN = (16, 9)
    ULTRAWIDE = (21, 9)

def largest_dimensions_for_aspect_ratio(video_files, desired_aspect_ratio):
    """
    Returns the largest dimensions possible for a group of videos and the specified aspect ratio
    """
    # Get videos
    music_video_dimensions = None
    largest_widescreen_dimensions = None
    videos = v_util.get_videos(video_files)
    logging.debug("\n")

    unique_dimensions = set()

    for video in videos:
        closest_widescreen_dimensions = None
        unique_dimensions.add((video.w, video.h))

        logging.debug(video.src_video_file)
        logging.debug("dimensions: {}".format(video.size))

        # Crop sides
        if video.aspect_ratio > desired_aspect_ratio:
            cropped_width = int(desired_aspect_ratio * video.h)
            closest_widescreen_dimensions = (cropped_width, video.h)
        # Crop top & bottom
        elif video.aspect_ratio < desired_aspect_ratio:
            cropped_height = int(video.w/desired_aspect_ratio)
            closest_widescreen_dimensions = (video.w, cropped_height)
        else:
            closest_widescreen_dimensions = (video.w, video.h)

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