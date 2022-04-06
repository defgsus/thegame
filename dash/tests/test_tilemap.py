import unittest

from dash.map import TileMap


class TestTilemap(unittest.TestCase):

    def test_window(self):
        map = TileMap((4, 3))
        map.fill(1)
        self.assertEqual(
            [[1, 1, 1, 1, 0, 0, 0, 0],
             [1, 1, 1, 1, 0, 0, 0, 0],
             [1, 1, 1, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]],
            map.get_window(0, 0, 8, 8)[:, :, 0].tolist()
        )
        self.assertEqual(
            [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 1, 1, 1, 1, 0, 0, 0],
             [0, 1, 1, 1, 1, 0, 0, 0],
             [0, 1, 1, 1, 1, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]],
            map.get_window(-1, -2, 8, 8)[:, :, 0].tolist()
        )
        self.assertEqual(
            [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 1, 1, 1],
             [0, 1, 1, 1]],
            map.get_window(-1, -2, 4, 4)[:, :, 0].tolist()
        )
        self.assertEqual(
            [[1, 1],
             [1, 1]],
            map.get_window(1, 1, 2, 2)[:, :, 0].tolist()
        )

