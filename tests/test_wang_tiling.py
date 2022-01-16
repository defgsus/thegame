import os
import unittest
import random
from typing import Optional

import numpy as np

from lib.gen import *
from .util import Timer, assert_numpy_equal

T = WangTiling.TOP
B = WangTiling.BOTTOM
L = WangTiling.LEFT
R = WangTiling.RIGHT

TL = WangTiling.TOP_LEFT
TR = WangTiling.TOP_RIGHT
BL = WangTiling.BOTTOM_LEFT
BR = WangTiling.BOTTOM_RIGHT


class TestWangTiling(unittest.TestCase):

    def assertEqualWangIndices(self, expected: np.ndarray, real: np.ndarray):
        self.assertEqual(
            expected.tolist(),
            real.tolist(),
            f"\nExpected:\n{WangTiling.to_string(expected)}"
            f"\nGot:\n{WangTiling.to_string(real)}"
        )

    def test_000_edge_indices(self):
        map = np.array([
            [0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0],
        ], dtype="int32")

        expected_edge_indices = np.array([
            [0, B  , 0  , 0  , 0],
            [R, B  , B|L, B  , 0],
            [R, T|R, R|L, L|B, L],
            [0, T  , T|R, T  , L],
            [0, 0  , 0  , T  , 0],
        ], dtype="int32")
        edge_indices = WangTiling.get_edge_indices(map)
        self.assertEqualWangIndices(expected_edge_indices, edge_indices)

        expected_layout_indices = [
            [0, 12 , 0  , 0  , 0],
            [1, 12 , 15 , 12 , 0],
            [1, 5  , 2  , 15 , 3],
            [0, 4  , 5  , 4  , 3],
            [0, 0  , 0  , 4  , 0],
        ]
        layout_indices = WangTiling.to_layout_indices(edge_indices)
        self.assertEqual(expected_layout_indices, layout_indices.tolist())

        self.assertEqual(
            [
                ["",  "B"  , ""   , ""   , ""],
                ["R", "B"  , "B|L", "B"  , ""],
                ["R", "T|R", "R|L", "B|L", "L"],
                ["",  "T"  , "T|R", "T"  , "L"],
                ["",  ""   , ""   , "T"  , ""],
            ],
            WangTiling.to_string(edge_indices).tolist()
        )

        expected_corner_indices = np.array([
            [BR   , 0    , BL   , 0    , 0    ],
            [BR   , BR   , BL|BR, BL   , BL   ],
            [TR   , 0    , TL|BR, 0    , BL   ],
            [TR   , TR   , TL|TR, TL   , TL   ],
            [0    , 0    , TR   , 0    , TL   ],
        ], dtype="int32")
        corner_indices = WangTiling.get_corner_indices(map)
        self.assertEqualWangIndices(expected_corner_indices, corner_indices)

        assert_numpy_equal(
            edge_indices | corner_indices,
            WangTiling.get_indices(map)
        )

    def test_001_edge_indices(self):
        map = np.array([
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ], dtype="int32")

        expected_edge_indices = np.array([
            [0, B    , B      , B    , 0],
            [R, B|R  , B|L|R  , B|L  , L],
            [R, T|B|R, T|B|L|R, T|B|L, L],
            [R, T|R  , T|L|R  , T|L  , L],
            [0, T    , T      , T    , 0],
        ], dtype="int32")
        edge_indices = WangTiling.get_edge_indices(map)
        self.assertEqualWangIndices(expected_edge_indices, edge_indices)

        # test bottom-up mapping as well
        expected_edge_indices_bottom_up = np.array([
            [0, T    , T      , T    , 0],
            [R, T|R  , T|L|R  , T|L  , L],
            [R, B|T|R, B|T|L|R, B|T|L, L],
            [R, B|R  , B|L|R  , B|L  , L],
            [0, B    , B      , B    , 0],
        ], dtype="int32")
        edge_indices_bottom_up = WangTiling.get_edge_indices(map, bottom_up=True)
        self.assertEqualWangIndices(expected_edge_indices_bottom_up, edge_indices_bottom_up)

    def test_001_edge_indices_layout(self):
        map = np.array([
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ], dtype="int32")

        expected_layout_indices = np.array([
            [0, 12   , 12  , 12  , 0],
            [1, 10   , 10  , 10  , 3],
            [1, 10   , 10  , 10  , 3],
            [1, 10   , 10  , 10  , 3],
            [0, 4    , 4   , 4   , 0],
        ], dtype="int32")
        edge_indices = WangTiling.get_edge_indices(map)
        layout_indices = WangTiling.to_layout_indices(
            edge_indices, occupied_mask=map.astype("bool")
        )
        assert_numpy_equal(
            expected_layout_indices,#.tolist(),
            layout_indices#.tolist()
        )
