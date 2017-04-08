class FFMPEGError(Exception):
    def __init__(self, message, return_code, stdout, stderr):

        # Initialize base exception class constructor
        super().__init__(message)

        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr