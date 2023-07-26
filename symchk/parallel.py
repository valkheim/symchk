import ctypes
import functools
import multiprocessing
import time
from typing import Any


def rate_limit(max_per_second: int) -> Any:
    min_interval = 1.0 / max_per_second
    lock = multiprocessing.Lock()
    last_time_called = multiprocessing.Value(ctypes.c_longdouble, time.time())

    def decorate(func):
        @functools.wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            with lock:
                elapsed = time.time() - last_time_called.value
                left_to_wait = min_interval - elapsed
                if left_to_wait > 0:
                    time.sleep(left_to_wait)

                ret = func(*args, **kwargs)
                last_time_called.value = time.time()
                return ret

        return wrapped

    return decorate
