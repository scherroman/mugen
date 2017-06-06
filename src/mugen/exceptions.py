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


class FFMPEGError(MugenError):
    """
    Exception class for ffmpeg errors
    """
    def __init__(self, message, return_code, stdout, stderr):

        # Initialize base exception class constructor
        super().__init__(message)

        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


