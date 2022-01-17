import os
import unittest
import random
from typing import Optional

import numpy as np

from lib.gen import *
from .util import Timer, assert_numpy_equal


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

    def test_ca_zoom(self):
        sampler = AutomatonSampler2D(block_size=16)
        expect = sampler.get_block_cached(0, 0)
        for x, y in (
                (0, 0), (-1, 3), (15, 17)
        ):
            w, h = expect.shape[1], expect.shape[0]
            if (x, y) != (0, 0):
                expect = sampler(x, y, w, h)
            for i in range(1, sampler.block_size + 1):
                area = sampler(x-i, y-i, w+i*2, h+i*2)
                area_cut = area[i:-i, i:-i]

                assert_numpy_equal(
                    expect, area_cut,
                    f"for i={i}, sampler({x-i}, {y-i}, {w+i*w}, {h+i*2})"
                )


@unittest.skipIf(not os.environ.get("BENCHMARK"), "define BENCHMARK to run")
class TestRandomSamplerBenchmark(unittest.TestCase):
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
            "pnoise128-1": self.benchmark(NoiseSampler2D(resolution=1, block_size=128), num_frames=100),
            "pnoise128-32": self.benchmark(NoiseSampler2D(resolution=32, block_size=128), num_frames=100),
            "pnoise128-128": self.benchmark(NoiseSampler2D(resolution=128, block_size=128), num_frames=100),
        }
        print()
        for sampler, timers in data.items():
            for task, timer in timers.items():
                print(
                    f"{sampler:16} {task:16} {timer.seconds():10} total sec "
                    f"{timer.fps():10,.0f} fps {timer.spf()*1000.:10.1f} ms"
                )
