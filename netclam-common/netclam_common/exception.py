"""Module providing exceptions used by NetClam OSS."""

class MySQLConnectionException(Exception):
    """Exception covering MySQL connection errors."""

    def __init__(self, *args: object) -> None:
        """Standard Exception Construct
        """
        super().__init__(*args)

class FileNotFoundException(Exception):
    """Exception covering NetClam file not found."""

    def __init__(self, *args: object) -> None:
        """Standard Exception Contruct
        """
        super().__init__(*args)

class RequestNotFoundException(Exception):
    """Exception covering NetClam request not found."""

    def __init__(self, *args: object) -> None:
        """Standard Exception Contruct
        """
        super().__init__(*args)

class ResultNotFoundException(Exception):
    """Exception covering NetClam result not found."""

    def __init__(self, *args: object) -> None:
        """Standard Exception Contruct
        """
        super().__init__(*args)
