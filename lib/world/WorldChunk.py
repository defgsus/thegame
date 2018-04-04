from lib.geom.TriangleMesh import TriangleMesh


class WorldBlock:
    def __init__(self):
        self.space_type = 0


class WorldChunk:

    LEFT = 1
    RIGHT = 2
    FRONT = 3
    BACK = 4
    BOTTOM = 5
    TOP = 6

    def __init__(self, tileset):
        self.num_x = 0
        self.num_y = 0
        self.num_z = 0
        self.blocks = []
        self.tileset = tileset

    def from_heightmap(self, heightmap):
        import random
        self.num_x = len(heightmap[0])
        self.num_y = len(heightmap)
        self.num_z = max(max(row) for row in heightmap) + 1
        self.blocks = []
        for z in range(self.num_z):
            plane = []
            for y in range(self.num_y):
                row = []
                for x in range(self.num_x):
                    block = WorldBlock()
                    h = heightmap[y][x]
                    block.space_type = 1 if h >= z else 0
                    block.texture = random.randrange(self.tileset.num_tiles)
                    row.append(block)
                plane.append(row)
            self.blocks.append(plane)

    def block(self, x, y, z):
        if 0 <= z < len(self.blocks):
            plane = self.blocks[z]
            if 0 <= y < len(plane):
                row = plane[y]
                if 0 <= x < len(row):
                    return row[x]
        return WorldBlock()

    def is_wall(self, x, y, z, dir):
        b = self.block(x, y, z)
        if b.space_type:
            return True
        return False

    def create_mesh(self):
        mesh = TriangleMesh()
        for z in range(self.num_z):
            z1 = z + 1
            for y in range(self.num_y):
                y1 = y + 1
                for x in range(self.num_x):
                    x1 = x + 1
                    b = self.block(x, y, z)
                    if b.space_type:
                        uvquad = self.tileset.get_uv_quad(b.texture)
                        # bottom
                        if not self.is_wall(x, y, z-1, self.TOP):
                            mesh.add_quad((x, y1, z), (x1, y1, z), (x1, y, z), (x, y, z), *uvquad)
                        # top
                        if not self.is_wall(x, y, z+1, self.BOTTOM):
                            mesh.add_quad((x, y, z1), (x1, y, z1), (x1, y1, z1), (x, y1, z1), *uvquad)
                        # front
                        if not self.is_wall(x, y-1, z, self.BACK):
                            mesh.add_quad((x, y, z), (x1, y, z), (x1, y, z1), (x, y, z1), *uvquad)
                        # back
                        if not self.is_wall(x, y+1, z, self.FRONT):
                            mesh.add_quad((x, y1, z), (x1, y1, z), (x1, y1, z1), (x, y1, z1), *uvquad)
                        # left
                        if not self.is_wall(x-1, y, z, self.RIGHT):
                            mesh.add_quad((x, y1, z), (x, y, z), (x, y, z1), (x, y1, z1), *uvquad)
                        # right
                        if not self.is_wall(x+1, y, z, self.LEFT):
                            mesh.add_quad((x1, y, z), (x1, y1, z), (x1, y1, z1), (x1, y, z1), *uvquad)
        return mesh
