from typing import Optional


class FilterBase:

    def __call__(self, value: float) -> float:
        raise NotImplementedError


class FollowFilter(FilterBase):

    def __init__(self, follow_up: float, follow_down: Optional[float] = None):
        self.follow_up = follow_up
        self.follow_down = follow_up if follow_down is None else follow_down
        self._value = 0.

    def __call__(self, value: float) -> float:
        if value > self._value:
            factor = self.follow_up
        else:
            factor = self.follow_down

        self._value += (value - self._value) * factor
        return self._value
