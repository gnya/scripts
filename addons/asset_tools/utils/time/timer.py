import time

from functools import wraps


class StopWatch:
    def __init__(self, name: str, logger: callable = print):
        self.name = name
        self.logger = logger

    def start(self):
        self.time_start = time.perf_counter()

    def stop(self):
        self.time_end = time.perf_counter()
        micros = (self.time_end - self.time_start) * 1000 * 1000

        self.logger(f'{self.name}: {round(micros, 1)} us')

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        self.stop()


def stopwatch(loops: int = 1, logger: callable = print) -> callable:
    def stopwatch_wrapper(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> callable:
            with StopWatch(func.__name__, logger):
                if loops > 1:
                    for _ in range(loops - 1):
                        func(*args, **kwargs)

                return func(*args, **kwargs)

        return wrapper

    return stopwatch_wrapper


def start_stopwatch(name: str, logger: callable = print) -> StopWatch:
    timer = StopWatch(name, logger)
    timer.start()

    return timer
