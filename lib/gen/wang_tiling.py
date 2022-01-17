from typing import Iterable, Union, Optional

import numpy as np
from numpy.random import Generator, PCG64, SeedSequence

from .sampler2d import BlockSampler2DBase
from .rand2d import RandomSampler2D


class WangTiling:
    TOP =    T = 1
    RIGHT =  R = 2
    BOTTOM = B = 4
    LEFT =   L = 8

    TOP_LEFT =     TL = 16
    TOP_RIGHT =    TR = 32
    BOTTOM_LEFT =  BL = 64
    BOTTOM_RIGHT = BR = 128

    EDGE_MASK = T | L | B | R
    CORNER_MASK = TL | TR | BL | BR

    NAMES = {
        T: "T",
        R: "R",
        B: "B",
        L: "L",
        TL: "TL",
        TR: "TR",
        BL: "BL",
        BR: "BR",
    }

    # TODO: move somewhere else
    #   This is the mapping of wang index to the 2-edge layout used on cr31.co.uk
    WANG_IDX_TO_LAYOUT_IDX = {
        0: 0,
        TOP: 4,
        RIGHT: 1,
        BOTTOM: 12,
        LEFT: 3,
        TOP | RIGHT: 5,
        TOP | LEFT: 7,
        BOTTOM | RIGHT: 13,
        BOTTOM | LEFT: 15,
        TOP | BOTTOM: 8,
        LEFT | RIGHT: 2,
        LEFT | BOTTOM | RIGHT: 14,
        LEFT | TOP | RIGHT: 6,
        TOP | BOTTOM | RIGHT: 9,
        TOP | BOTTOM | LEFT: 11,
        TOP | RIGHT | BOTTOM | LEFT: 10,
    }

    @classmethod
    def to_string(cls, x: Union[int, np.ndarray]) -> Union[str, np.ndarray]:
        if isinstance(x, np.ndarray):
            return np.vectorize(cls.to_string)(x)

        flags = [
            name
            for flag, name in cls.NAMES.items()
            if x & flag
        ]
        return "|".join(flags)

    @classmethod
    def get_edge_indices(cls, map: np.ndarray, bottom_up: bool = False, include_occupied: bool = True) -> np.ndarray:
        occupied = np.pad(map, [1, 1])
        indices = cls._get_edge_indices(occupied, bottom_up=bottom_up)
        if include_occupied:
            indices |= map * cls.EDGE_MASK
        return indices

    @classmethod
    def get_corner_indices(cls, map: np.ndarray, bottom_up: bool = False, include_occupied: bool = True) -> np.ndarray:
        occupied = np.pad(map, [1, 1])
        indices = cls._get_corner_indices(occupied, bottom_up=bottom_up)
        if include_occupied:
            indices |= map * cls.CORNER_MASK
        return indices

    @classmethod
    def get_indices(cls, map: np.ndarray, bottom_up: bool = False, include_occupied: bool = True) -> np.ndarray:
        occupied = np.pad(map, [1, 1])
        edges = cls._get_edge_indices(occupied, bottom_up=bottom_up)
        corners = cls._get_corner_indices(occupied, bottom_up=bottom_up)
        indices = edges | corners
        if include_occupied:
            indices |= map * (cls.EDGE_MASK | cls.CORNER_MASK)
        return indices

    @classmethod
    def to_layout_indices(
            cls,
            indices: np.ndarray,
    ) -> np.ndarray:
        layout_indices = np.zeros_like(indices)
        for wang_idx, layout_idx in cls.WANG_IDX_TO_LAYOUT_IDX.items():
            layout_indices[indices == wang_idx] = layout_idx

        return layout_indices

    @classmethod
    def _get_edge_indices(cls, occupied: np.ndarray, bottom_up: bool = False) -> np.ndarray:
        if bottom_up:
            t = occupied[2:  , 1:-1] * cls.TOP
            b = occupied[ :-2, 1:-1] * cls.BOTTOM
        else:
            t = occupied[ :-2, 1:-1] * cls.TOP
            b = occupied[2:  , 1:-1] * cls.BOTTOM
        l = occupied[1:-1,  :-2] * cls.LEFT
        r = occupied[1:-1, 2:  ] * cls.RIGHT
        return t | b | l | r

    @classmethod
    def _get_corner_indices(cls, occupied: np.ndarray, bottom_up: bool = False) -> np.ndarray:
        if bottom_up:
            tl = occupied[2:  ,  :-2] * cls.TOP_LEFT
            tr = occupied[2:  , 2:  ] * cls.TOP_RIGHT
            bl = occupied[ :-2,  :-2] * cls.BOTTOM_LEFT
            br = occupied[ :-2, 2:  ] * cls.BOTTOM_RIGHT
        else:
            tl = occupied[ :-2,  :-2] * cls.TOP_LEFT
            tr = occupied[ :-2, 2:  ] * cls.TOP_RIGHT
            bl = occupied[2:  ,  :-2] * cls.BOTTOM_LEFT
            br = occupied[2:  , 2:  ] * cls.BOTTOM_RIGHT

        return tl | tr | bl | br

