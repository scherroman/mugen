def seconds_to_time_code(seconds: float) -> str:
    ms = 1000 * round(seconds - int(seconds), 3)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d.%03d" % (h, m, s, ms)
