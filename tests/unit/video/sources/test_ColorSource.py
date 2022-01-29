from mugen.video.sources.ColorSource import ColorSource


def get_black_source() -> ColorSource:
    return ColorSource('black')


def get_white_source() -> ColorSource:
    return ColorSource('white')


def get_orange_source() -> ColorSource:
    return ColorSource('#FFA500')


def get_purple_source() -> ColorSource:
    return ColorSource('#800080')
