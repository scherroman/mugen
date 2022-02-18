from mugen.video.segments.ColorSegment import ColorSegment


def get_black_segment() -> ColorSegment:
    return ColorSegment("black", 1, (720, 540))


def get_white_segment() -> ColorSegment:
    return ColorSegment("white", 1, (1920, 1080))


def get_orange_segment() -> ColorSegment:
    return ColorSegment("#FF4500", 1, (300, 300))
