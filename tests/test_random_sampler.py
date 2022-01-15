import unittest
import random
from typing import Optional

import numpy as np

from lib.gen import *
from .util import Timer


class TestRandomSampler(unittest.TestCase):

    # Ahem.. for now this test needs visual inspection and
    #   comparison with the area test below
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
                (h, w), block.shape,
                f"for {x}, {y}, {w}, {h} at block_size {rs.block_size}"
            )

    def benchmark(self, sampler: BlockSampler2DBase, num_frames: int = 300):
        ret = dict()
        with Timer(num_frames) as timer:
            for i in range(num_frames):
                sampler.get_block(i // 10, i // 11)
        ret["block"] = timer

        with Timer(num_frames) as timer:
            for i in range(num_frames):
                sampler.get_block_cached(i // 10, i // 11)
        ret["block_cached"] = timer

        with Timer(num_frames) as timer:
            for i in range(num_frames):
                sampler(i // 10, i // 11, sampler.block_size * 2, sampler.block_size * 2)
        ret["area"] = timer

        rnd = random.Random(42)
        with Timer(num_frames) as timer:
            for i in range(num_frames):
                sampler(rnd.randint(-20, 20), rnd.randint(-20, 20), sampler.block_size * 2, sampler.block_size * 2)
        ret["area random"] = timer
        return ret

    def test_benchmark(self):
        data = {
            "rnd32": self.benchmark(RandomSampler2D(block_size=32)),
            "automat32": self.benchmark(AutomatonSampler2D(block_size=32), num_frames=20),
            "automat64": self.benchmark(AutomatonSampler2D(block_size=64), num_frames=10),
        }
        print()
        for sampler, timers in data.items():
            for task, timer in timers.items():
                print(
                    f"{sampler:10} {task:20} {timer.seconds():10} total sec "
                    f"{timer.fps():10} fps {timer.spf()*1000.:10} ms"
                )
