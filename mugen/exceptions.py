class MugenError(Exception):
    """
    The root mugen exception class
    """

    pass


class ParameterError(MugenError):
    """
    Exception class for mal-formed inputs
    """

    pass
