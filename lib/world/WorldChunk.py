import os
import glm
from pyglet.gl import *
from lib.geom import TriangleMesh
from lib.opengl import Texture3D
from .VoxelDistanceField import VoxelDistanceField


class WorldBlock:
    def __init__(self):
        self.space_type = 0
        self.texture = 0

    def __repr__(self):
        return "(%s)" % self.space_type


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
        self.filename = None

    def size(self):
        return self.num_x, self.num_y, self.num_z

    def from_heightmap(self, heightmap, do_flip_y=False):
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
                    h = heightmap[self.num_y-1-y][x] if do_flip_y else heightmap[y][x]
                    block.space_type = 1 if h >= z else 0
                    if block.space_type:
                        if h == 0:
                            block.texture = 0
                        else:
                            block.texture = random.randrange(1, self.tileset.num_tiles)
                    row.append(block)
                plane.append(row)
            self.blocks.append(plane)

    def from_tiled(self, tiled):
        """from TiledImport or filename"""
        if isinstance(tiled, str):
            from .TiledImport import TiledImport
            self.filename = tiled
            tiled = TiledImport()
            tiled.load(self.filename)

        self.num_x = tiled.width
        self.num_y = tiled.height
        self.num_z = tiled.num_layers
        self.blocks = []
        for z in range(self.num_z):
            plane = []
            for y in range(self.num_y):
                row = []
                for x in range(self.num_x):
                    block = WorldBlock()
                    tex = tiled.layers[z][(self.num_y-1-y)*self.num_x+x]
                    block.texture = max(0, tex - 1)
                    block.space_type = tex > 0
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

    def is_wall(self, x, y, z, side):
        b = self.block(x, y, z)
        if b.space_type:
            return True
        return False

    def density_at(self, x, y, z, radius=1):
        dens = 0.
        for z in range(z - radius, z + radius + 1):
            for y in range(y - radius, y + radius + 1):
                for x in range(x - radius, x + radius + 1):
                    if self.block(x, y, z).space_type:
                        dens += 1.
        return dens / pow(1 + 2 * radius, 3)

    def create_texture3d(self):
        tex = Texture3D(name="voxels")
        tex.create()
        tex = self.update_texture3d(tex)
        print("voxels", tex)
        return tex

    def update_texture3d(self, tex):
        values = []
        max_dens = 0.
        for z, plane in enumerate(self.blocks):
            for y, row in enumerate(plane):
                for x, b in enumerate(row):
                    values.append(b.space_type)
                    values.append(self.density_at(x, y, z))
                    max_dens = max(max_dens, values[-1])
                    values.append(0.)
        if max_dens:
            for i in range(1, len(values), 3):
                values[i] /= max_dens

        tex.bind()
        tex.upload(values, self.num_x, self.num_y, self.num_z, GL_RGB, GL_FLOAT)
        return tex

    def create_mesh(self):
        mesh = TriangleMesh()
        mesh.create_attribute("a_ambient", 3)

        def add_quad(p1, p2, p3, p4, *uvquad):
            mesh.add_quad(p1, p2, p3, p4, *uvquad)
            for p in (p1, p2, p3, p1, p3, p4):
                mesh.add_attribute("a_ambient", self.get_ambient_color(*p))

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
                            add_quad((x, y1, z), (x1, y1, z), (x1, y, z), (x, y, z), *uvquad)
                        # top
                        if not self.is_wall(x, y, z+1, self.BOTTOM):
                            add_quad((x, y, z1), (x1, y, z1), (x1, y1, z1), (x, y1, z1), *uvquad)
                        # front
                        if not self.is_wall(x, y-1, z, self.BACK):
                            add_quad((x, y, z), (x1, y, z), (x1, y, z1), (x, y, z1), *uvquad)
                        # back
                        if not self.is_wall(x, y+1, z, self.FRONT):
                            add_quad((x, y1, z), (x, y1, z1), (x1, y1, z1), (x1, y1, z), *uvquad)
                        # left
                        if not self.is_wall(x-1, y, z, self.RIGHT):
                            add_quad((x, y1, z), (x, y, z), (x, y, z1), (x, y1, z1), *uvquad)
                        # right
                        if not self.is_wall(x+1, y, z, self.LEFT):
                            add_quad((x1, y, z), (x1, y1, z), (x1, y1, z1), (x1, y, z1), *uvquad)

        #print("LEN", len(mesh._vertices), len(mesh._attributes["a_ambient"]["values"]))
        return mesh

    def get_ambient_color(self, x, y, z):
        tests = (
            (x-1, y+0, z+0, self.RIGHT),
            (x-1, y-1, z+0, self.RIGHT),
            (x+0, y+0, z+0, self.LEFT),
            (x+0, y-1, z+0, self.LEFT),

            (x-1, y-1, z+1, self.BOTTOM),
            (x+0, y-1, z+1, self.BOTTOM),
            (x-1, y+0, z+1, self.BOTTOM),
            (x+0, y+0, z+1, self.BOTTOM),

            (x-1, y-1, z+2, self.BOTTOM),
            (x+0, y-1, z+2, self.BOTTOM),
            (x-1, y+0, z+2, self.BOTTOM),
            (x+0, y+0, z+2, self.BOTTOM),

            (x-2, y-2, z+3, self.BOTTOM),
            (x-1, y-2, z+3, self.BOTTOM),
            (x+0, y-2, z+3, self.BOTTOM),
            (x+1, y-2, z+3, self.BOTTOM),

            (x-2, y-1, z+3, self.BOTTOM),
            (x-1, y-1, z+3, self.BOTTOM),
            (x+0, y-1, z+3, self.BOTTOM),
            (x+1, y-1, z+3, self.BOTTOM),

            (x-2, y+0, z+3, self.BOTTOM),
            (x-1, y+0, z+3, self.BOTTOM),
            (x+0, y+0, z+3, self.BOTTOM),
            (x+1, y+0, z+3, self.BOTTOM),

            (x-2, y+1, z+3, self.BOTTOM),
            (x-1, y+1, z+3, self.BOTTOM),
            (x+0, y+1, z+3, self.BOTTOM),
            (x+1, y+1, z+3, self.BOTTOM),
        )
        count = 0
        for t in tests:
            if self.is_wall(*t):
                count += 1
        count = 1. - count / len(tests)
        return (count, count, count)

    def create_voxel_distance_field(self, scale):
        if self.filename:
            cache_filename = "%s-cached-sdf.json" % self.filename
            if os.path.exists(cache_filename):
                if os.path.getmtime(cache_filename) >= os.path.getmtime(self.filename):
                    vox = VoxelDistanceField(0,0,0)
                    vox.load_json(cache_filename)
                    return vox

        vox = VoxelDistanceField(self.num_x*scale, self.num_y*scale, self.num_z*scale)
        for z in range(self.num_z):
            for y in range(self.num_y):
                for x in range(self.num_x):
                    if self.block(x, y, z).space_type > 0:
                        for sz in range(scale):
                            for sy in range(scale):
                                for sx in range(scale):
                                    vox.set_value(x+sx, y+sy, z+sz, 1)
        vox.calc_distances()
        if self.filename:
            vox.save_json(cache_filename)
        return vox

    def cast_voxel_ray(self, ro, rd, max_steps=None):
        """
        iq, nijhoff, https://www.shadertoy.com/view/4ds3WS
        """
        if max_steps is None:
            max_steps = max(self.size())

        pos = glm.floor(ro)
        rd = glm.vec3(rd)
        rd += 0.0000001
        ri = 1. / rd
        rs = glm.sign(rd)
        dis = (pos - ro + .5 + rs*.5) * ri

        hit = False

        for i in range(max_steps):
            mm = glm.step(dis.xyz, dis.yxy) * glm.step(dis.xyz, dis.zzx)
            dis += mm * rs * ri
            pos += mm * rs
            if self.block(int(pos.x), int(pos.y), int(pos.z)).space_type:
                hit = True
                break

        #nor = -mm*rs

        mini = (pos-ro + 0.5 - 0.5*rs)*ri
        t = max(mini)

        return t, hit