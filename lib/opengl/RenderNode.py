from typing import List, Union

from .core.base import *
from .RenderSettings import RenderSettings


class RenderNode:

    def __init__(self, name: str):
        self.name = name
        self.is_created = False

    def __str__(self):
        return "%s('%s', created=%s, numcol=%s)" % (
            self.__class__.__name__,
            self.name, self.is_created, self.num_color_outputs(),
        )

    def num_color_outputs(self) -> int:
        return 1

    def has_depth_output(self) -> bool:
        return False

    def num_multi_sample(self) -> int:
        return 0

    def num_passes(self) -> int:
        return 1

    def output_slots(self) -> List[Union[int, str]]:
        s = list(range(self.num_color_outputs()))
        if self.has_depth_output():
            s.append("depth")
        return s

    def create(self, rs: RenderSettings):
        pass

    def release(self):
        pass

    def render(self, rs: RenderSettings, pass_num: int):
        raise NotImplementedError

    def update(self, rs: RenderSettings, dt: float):
        pass
