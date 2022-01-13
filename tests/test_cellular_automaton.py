import unittest

import numpy as np

from lib.ai.automaton import CellularAutomatonBase, ClassicAutomaton


class TestCellularAutomaton(unittest.TestCase):

    def test_total_neighbours(self):
        ca = CellularAutomatonBase(5, 5)
        ca.cells[:] = [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1],
            [0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0],
        ]
        total = ca.total_neighbours()
        self.assertEqual(
            [
                [0, 1, 2, 2, 1],
                [0, 2, 2, 3, 2],
                [0, 2, 2, 5, 2],
                [1, 2, 1, 3, 1],
                [0, 1, 0, 1, 1]
            ],
            total.tolist()
        )

    def test_classic(self):
        # https://en.wikipedia.org/wiki/Glider_(Conway's_Life)
        expected_sequence = [
            [
                [0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0, 0],
                [1, 0, 1, 0, 0],
                [0, 1, 1, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [1, 0, 1, 0, 0],
                [0, 1, 1, 0, 0],
                [0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 1, 1, 0],
                [0, 1, 1, 0, 0],
                [0, 0, 0, 0, 0],
            ],
        ]
        ca = ClassicAutomaton(5, 5)
        ca.cells[:] = expected_sequence[0]
        for seq in expected_sequence[1:]:
            ca.step()
            # print(ca.cells)
            self.assertEqual(seq, ca.cells.tolist())
