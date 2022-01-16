import random
from typing import Optional, Iterable, List

import numpy as np
import scipy.signal


class CellularAutomatonBase:

    def __init__(
            self,
            width: int = 16,
            height: int = 16,
            dtype: str = "int8",
            cells: Optional[np.ndarray] = None,
    ):
        if cells is not None:
            self.cells = cells
        else:
            self.cells = np.zeros([height, width], dtype=dtype)
        self._kernel = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ])

    @property
    def width(self) -> int:
        return self.cells.shape[-1]

    @property
    def height(self) -> int:
        return self.cells.shape[-2]

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
            width: int = 16,
            height: int = 16,
            born: Iterable[int] = (3,),
            survive: Iterable[int] = (2, 3),
            cells: Optional[np.ndarray] = None,
    ):
        super().__init__(width, height, cells=cells)
        self.born = set(born)
        self.survive = set(survive)

    def step(self, count: int = 1):
        new_cells = np.zeros([self.height, self.width], dtype="bool")
        for i in range(count):
            neigh = self.total_neighbours()
            dead = self.cells == 0
            alive = np.invert(dead)

            for num_n in self.born:
                new_cells |= dead & (neigh == num_n)
            for num_n in self.survive:
                new_cells |= alive & (neigh == num_n)

        self.cells = new_cells.astype(self.cells.dtype)

    def step_old(self, count: int = 1):
        """
        Don't use, this is the old python-loop version
        """
        for i in range(count):
            neigh = self.total_neighbours()
            for y, row in enumerate(self.cells):
                for x, value in enumerate(row):
                    if not value:
                        if neigh[y][x] in self.born:
                            row[x] = 1
                    else:
                        if neigh[y][x] not in self.survive:
                            row[x] = 0
