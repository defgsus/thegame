import random
from typing import Optional, Iterable, List

import numpy as np
import scipy.signal


class CellularAutomatonBase:

    def __init__(self, width: int, height: int, dtype: str = "int8"):
        self.width = width
        self.height = height
        self.cells = np.zeros([self.height, self.width], dtype=dtype)
        self._kernel = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ])

    def step(self):
        raise NotImplementedError

    def cell(self, x: int, y: int) -> int:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return 0

    def total_neighbours(self) -> np.ndarray:
        total = scipy.signal.convolve2d(self.cells, self._kernel)
        return total[1:-1, 1:-1]

    def init_random(self, probability: float = .5, seed: Optional[int] = None):
        rnd = random.Random(seed)
        for i in range(100):
            rnd.getrandbits(8)
        for row in self.cells:
            for i in range(self.width):
                row[i] = 1 if random.random() < probability else 0


class ClassicAutomaton(CellularAutomatonBase):

    def __init__(
            self,
            width: int,
            height: int,
            born: Iterable[int] = (3,),
            survive: Iterable[int] = (2, 3),
    ):
        super().__init__(width, height)
        self.born = set(born)
        self.survive = set(survive)

    def step(self):
        neigh = self.total_neighbours()
        for y, row in enumerate(self.cells):
            for x, value in enumerate(row):
                if not value:
                    if neigh[y][x] in self.born:
                        row[x] = 1
                else:
                    if neigh[y][x] not in self.survive:
                        row[x] = 0
