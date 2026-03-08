import time
from functools import wraps
from types import TracebackType
from typing import Any, Callable


class StopWatch:
    def __init__(self, name: str, logger: Callable[[str], None] = print):
        self.name = name
        self.logger = logger

    def start(self):
        self.time_start = time.perf_counter()

    def stop(self):
        self.time_end = time.perf_counter()
        micros = (self.time_end - self.time_start) * 1000 * 1000

        self.logger(f"{self.name}: {round(micros, 1)} us")

    def __enter__(self):
        self.start()

    def __exit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ):
        self.stop()


def stopwatch(
    loops: int = 1, logger: Callable[[str], None] = print
) -> Callable[..., Any]:
    def stopwatch_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Callable[..., Any]:
            with StopWatch(func.__name__, logger):
                if loops > 1:
                    for _ in range(loops - 1):
                        func(*args, **kwargs)

                return func(*args, **kwargs)

        return wrapper

    return stopwatch_wrapper


def start_stopwatch(name: str, logger: Callable[[str], None] = print) -> StopWatch:
    timer = StopWatch(name, logger)
    timer.start()

    return timer
