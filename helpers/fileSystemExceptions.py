class BasePathException(OSError):
    def __init__(self, path):
        self._path = path


class IsNotDirectoryException(BasePathException):
    def __str__(self):
        return f"<{self._path}> is not directory"


class IsNotEmptyException(BasePathException):
    def __str__(self):
        return f"Directory <{self._path}> is not empty"


class PathExistsException(BasePathException):
    def __str__(self):
        return f"Path <{self._path}> exists"


class PathExistsAsFileException(BasePathException):
    def __str__(self):
        return f"Path <{self._path}> exists as file, not as a directory"


class PathExistsAsDirectoryException(BasePathException):
    def __str__(self):
        return f"Path <{self._path}> exists as directory, not as a file"


class PathNotFoundException(BasePathException):
    def __str__(self):
        return f"Path <{self._path}> not found"
