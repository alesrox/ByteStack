import sys

class CompilationException(BaseException):
    def __init__(self, message):
        sys.tracebacklimit = 0
        super().__init__(message)

class ParserError(CompilationException):
    def __init__(self, message: str):
        super().__init__(message)

class SemanticError(CompilationException):
    def __init__(self, message: str, lineno: int = 0):
        super().__init__(f"{message} at line {lineno}.")