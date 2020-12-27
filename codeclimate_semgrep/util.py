"""Utility functions"""
from typing import IO, Callable


def delimited_writer(out: IO[str], delimiter: str = "\0") -> Callable[[str], None]:
    """Create a function to write a string with a given delimiter to IO

    Args:
        out: The IO stream for writing.
        delimiter: The delimiter to insert between writes to `out`.
    Returns:
        A function that writes its argument, `data`, to `out`. A delimiter will
        be inserted between calls to the function, with no leading or trailing
        delimeters.
    """
    written = False

    def _writer(data: str):
        nonlocal written
        if written:
            out.write(delimiter)
        out.write(data)
        written = True

    return _writer
