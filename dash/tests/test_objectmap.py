import unittest

from dash.map import TileMap, Objects, Object


class TestObjectMap(unittest.TestCase):

    def test_window(self):
        tile_map = TileMap((10, 10))
        tile_map.set_outside(1, 0, 0, 0)
        object_map = Objects(tile_map)

        object_map.add_object("obj", (2.5, 2.5))
        object_map.add_object("obj", (3.5, 2.5))
        object_map.dump_objects()
        for i in range(2):
            object_map.update(0, 1./60.)
        object_map.dump_objects()
