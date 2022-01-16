import os
import unittest

from lib.gen.automaton import CellularAutomatonBase, ClassicAutomaton
from .util import Timer


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


@unittest.skipIf(not os.environ.get("BENCHMARK"), "define BENCHMARK to run")
class TestCABenchmark(unittest.TestCase):
    """
    gol32      total_neighbours         0.0106 total sec   28364.81 fps        0.0 ms
    gol32      step                     0.0148 total sec    20317.3 fps        0.0 ms
    gol32      step_old                 0.1076 total sec    2789.24 fps        0.4 ms
    ca32       total_neighbours         0.0106 total sec   28379.52 fps        0.0 ms
    ca32       step                     0.0307 total sec    9775.79 fps        0.1 ms
    ca32       step_old                 0.1475 total sec    2033.29 fps        0.5 ms
    ca128      total_neighbours         0.0983 total sec    2035.14 fps        0.5 ms
    ca128      step                     0.1589 total sec    1258.77 fps        0.8 ms
    ca128      step_old                 1.4437 total sec     138.53 fps        7.2 ms
    ca256      total_neighbours         0.2138 total sec     467.63 fps        2.1 ms
    ca256      step                     0.2883 total sec     346.83 fps        2.9 ms
    ca256      step_old                 2.8877 total sec      34.63 fps       28.9 ms
    """

    def benchmark(self, ca: ClassicAutomaton, num_frames: int = 300) -> dict:
        ret = dict()
        with Timer(num_frames) as timer:
            for i in range(num_frames):
                ca.total_neighbours()
        ret["total_neighbours"] = timer

        with Timer(num_frames) as timer:
            ca.step(num_frames)
        ret["step"] = timer

        with Timer(num_frames) as timer:
            ca.step_old(num_frames)
        ret["step_old"] = timer
        return ret

    def test_benchmark(self):
        born = set(range(9))
        survive = set(range(9))
        data = {
            "gol32": self.benchmark(ClassicAutomaton(32, 32), 300),
            "ca32": self.benchmark(ClassicAutomaton(32, 32, born=born, survive=survive), 300),
            "ca128": self.benchmark(ClassicAutomaton(128, 128, born=born, survive=survive), 200),
            "ca256": self.benchmark(ClassicAutomaton(256, 256, born=born, survive=survive), 100),
        }
        print()
        for sampler, timers in data.items():
            for task, timer in timers.items():
                print(
                    f"{sampler:10} {task:20} {timer.seconds():10} total sec "
                    f"{timer.fps():10} fps {timer.spf()*1000.:10} ms"
                )
