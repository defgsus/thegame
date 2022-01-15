import unittest
import random
from typing import Optional

import numpy as np

from lib.gen import RandomSampler2D


class TestRandomSampler(unittest.TestCase):

    def test_010_block(self):
        rs = RandomSampler2D(block_size=4)
        print("x")
        for i in range(3):
            block = (rs.get_block(i, 0) * 10).astype(int)
            print()
            print(block)
        print("y")
        for i in range(3):
            block = (rs.get_block(0, i) * 10).astype(int)
            print()
            print(block)

    def test_100_area(self):
        rs = RandomSampler2D(block_size=4)
        block = (rs(0, 0, 10, 10) * 10).astype(int)
        print(block)

    def test_110_area_shape_fuzz(self):
        rnd = random.Random(384739874)
        for i in range(1000):
            rs = RandomSampler2D(block_size=rnd.randint(2, 10))
            x = rnd.randint(-30, 30)
            y = rnd.randint(-30, 30)
            w = rnd.randint(1, 20)
            h = rnd.randint(1, 20)
            block = rs(x, y, w, h)
            self.assertEqual(
                #(h, w), block.shape,
                w, block.shape[-1],
                f"for {x}, {y}, {w}, {h} at block_size {rs.block_size}"
            )
