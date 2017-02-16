import tesserocr
from PIL import Image
from moviepy.video.tools.cuts import detect_scenes

# Project modules
import mugen.settings as s

def video_segment_is_repeat(video_segment, video_segments_used):
    """
    Checks if a video segment is a repeat of a video segment already used.
    Also returns the matching used segment
    """
    segment_overlaps = False
    used_segment_overlapped = None
    for used_segment in video_segments_used:
        start_overlaps = used_segment.src_start_time <= video_segment.src_start_time < used_segment.src_end_time
        end_overlaps = used_segment.src_start_time < video_segment.src_end_time <= used_segment.src_end_time
        if start_overlaps or end_overlaps:
            segment_overlaps = True
            used_segment_overlapped = used_segment

    return segment_overlaps

def video_segment_contains_scene_change(video_segment):
    """
    Checks if a video segment contains a scene change
    """
    cuts, luminosities = detect_scenes(video_segment, fps=s.MOVIEPY_FPS, progress_bar=False)

    return True if len(cuts) > 1 else False
        
def video_segment_contains_text(video_segment):
    """
    Checks if a video segment contains text
    """
    first_frame_contains_text = False
    last_frame_contains_text = False
    first_frame = video_segment.get_frame(t='00:00:00')
    last_frame = video_segment.get_frame(t=video_segment.duration)

    #Check first frame
    frame_image = Image.fromarray(first_frame)
    text = tesserocr.image_to_text(frame_image)
    if len(text.strip()) > 0:
        first_frame_contains_text = True

    #Check last frame
    frame_image = Image.fromarray(last_frame)
    text = tesserocr.image_to_text(frame_image)
    if len(text.strip()) > 0:
        last_frame_contains_text = True

    return True if first_frame_contains_text or last_frame_contains_text else False

def video_segment_contains_solid_color(video_segment):
    """
    Checks if a video segment contains a solid color or nearly a solid color
    """
    first_frame_is_solid_color = False
    last_frame_is_solid_color = False
    first_frame = video_segment.get_frame(t='00:00:00')
    last_frame = video_segment.get_frame(t=video_segment.duration)

    #Check first frame
    frame_image = Image.fromarray(first_frame)
    extrema = frame_image.convert("L").getextrema()
    if abs(extrema[1] - extrema[0]) <= s.MIN_EXTREMA_RANGE:
        first_frame_is_solid_color = True

    #Check last frame
    frame_image = Image.fromarray(last_frame)
    extrema = frame_image.convert("L").getextrema()
    if abs(extrema[1] - extrema[0]) <= s.MIN_EXTREMA_RANGE:
        last_frame_is_solid_color = True

    return True if first_frame_is_solid_color or last_frame_is_solid_color else False