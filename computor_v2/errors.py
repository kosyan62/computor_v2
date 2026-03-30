class ComputorError(Exception):
    def __init__(self, message="An error occurred"):
        super().__init__(message)


class ComputorNameError(ComputorError):
    def __init__(self, message="Undefined name"):
        super().__init__(message)


class ComputorArgumentError(ComputorError):
    def __init__(self, message="Wrong number of arguments"):
        super().__init__(message)


class ComputorTypeError(ComputorError):
    def __init__(self, message="Type error"):
        super().__init__(message)


class ComputorSolverError(ComputorError):
    def __init__(self, message="Cannot solve"):
        super().__init__(message)


class ComputorRecursionError(ComputorError):
    def __init__(self, message="Recursive call detected"):
        super().__init__(message)


class ComputorValueError(ComputorError):
    def __init__(self, message="Invalid value"):
        super().__init__(message)