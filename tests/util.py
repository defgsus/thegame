import time
from typing import Optional

import numpy as np


class Timer:

    def __init__(self, num_frames: int = 1):
        self.num_frames = num_frames

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()

    def __repr__(self):
        return f"{self.seconds()} sec, {self.fps()} fps"

    def seconds(self) -> float:
        return round(self.end_time - self.start_time, 4)

    def fps(self, num_frames: Optional[int] = None) -> float:
        seconds = self.end_time - self.start_time
        if not seconds:
            return 1000
        return round((num_frames or self.num_frames) / seconds, 2)

    def spf(self, num_frames: Optional[int] = None) -> float:
        seconds = self.end_time - self.start_time
        return round(seconds / (num_frames or self.num_frames), 4)


def assert_numpy_equal(
        expected, real,
        msg: Optional[str] = None
):
    message = f"\n\nExpected:\n{expected}\n\nGot:\n{real}"
    if msg:
        message = f"{message}\n{msg}"
    if expected.shape != real.shape:
        raise AssertionError(f"numpy shape {real.shape} not equal, expected {expected.shape}{message}")
    if not np.all(expected == real):
        raise AssertionError(
            f"numpy array values not equal{message}"
        )