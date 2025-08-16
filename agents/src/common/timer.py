"""Timer class.

Context and decorator form timer.
"""

import contextlib
from functools import wraps
from time import perf_counter

from src.common.logger import log_info, log_success


class Timer(contextlib.ContextDecorator):
    """Timer.

    Examples:
        >>> with Timer('Code1'):
        ...     sleep(1)
        * Code1        | 1.00s (0.02m)
    """

    def __init__(self, name="Elapsed time"):
        self.name = name

    def __enter__(self):
        log_info(f"{self.name:20}", prefix="START")
        self.start_time = perf_counter()
        return self

    def __exit__(self, *exc):
        elapsed_time = perf_counter() - self.start_time
        log_success(f"{self.name} ({elapsed_time/60:.2f}m)")
        return False


def T(fn: callable) -> callable:
    """Timer decorator.

    Example:
        >>> @T
        >>> def f():
        ...     sleep(1)
        * Elapsed time | 1.00s (0.02m)
    """

    @wraps(fn)
    def _log(*args, **kwargs):
        with Timer(fn.__name__):
            rst = fn(*args, **kwargs)
        return rst

    return _log
