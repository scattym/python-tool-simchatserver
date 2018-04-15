class Error(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message=None):
        if message:
            self.message = message
        else:
            self.message = "A generic error occurred"


class ProtocolError(Error):
    """Exception raised for errors in the login.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class LoginError(Error):
    """Exception raised for errors in the login.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class ClientClosedError(Error):
    """Exception raised for errors in the login.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message