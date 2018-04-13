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

    LEFT = 1<<0
    RIGHT = 1<<1
    FRONT = 1<<2
    BACK = 1<<3
    BOTTOM = 1<<4
    TOP = 1<<5

    def __init__(self, tileset):
        self.num_x = 0
        self.num_y = 0
        self.num_z = 0
        self.blocks = []
        self.tileset = tileset
        self.filename = None
        self._waypoints = None

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

    def is_occupied(self, x, y, z):
        return self.block(x, y, z).space_type != 0

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

    @property
    def waypoints(self):
        if self._waypoints is None:
            self._waypoints = self.create_waypoints()
        return self._waypoints

    def create_waypoints_old(self, steps=1):
        from ..ai import WayPoints
        wp = WayPoints()
        z = 1
        for y in range(0, self.num_y, steps):
            for x in range(0, self.num_x, steps):
                if self.block(x, y, z).space_type == 0:
                    doit = True
                    for x1 in range(x, x + steps + 1):
                        if self.block(x1, y, z).space_type != 0:
                            doit = False
                            break
                    if doit:
                        wp.add_edge_pos((x, y, z), (x + steps, y, z))

                    doit = True
                    for y1 in range(y, y+steps+1):
                        if self.block(x, y1, z).space_type != 0:
                            doit = False
                            break
                    if doit:
                        wp.add_edge_pos((x, y, z), (x, y+steps, z))

                    if steps > 0:
                        doit = True
                        for i in range(steps+1):
                            if self.block(x+i, y+i, z).space_type != 0 or \
                                    (self.block(x+i+1, y+i, z).space_type != 0 and
                                     self.block(x+i, y+i+1, z).space_type != 0):
                                doit = False
                                break
                        if doit:
                            wp.add_edge_pos((x, y, z), (x+steps, y+steps, z))

                        doit = True
                        for i in range(steps+1):
                            if self.block(x+i, y-i, z).space_type != 0 or \
                                    (self.block(x+i+1, y-i, z).space_type != 0 and
                                     self.block(x+i, y-i-1, z).space_type != 0):
                                doit = False
                                break
                        if doit:
                            wp.add_edge_pos((x, y, z), (x+steps, y-steps, z))

        print("waypoints", wp.num_nodes, wp.num_edges)
        return wp

    def create_waypoints(self):
        """floodfill"""
        from ..ai import WayPoints
        wp = WayPoints()
        # find start pos
        x, y, z = 2, 2, self.num_z+1
        while not self.is_wall(x, y, z-1, self.TOP):
            z -= 1

        visited = set()
        visit = {(x, y, z)}

        while visit:
            cur = visit.pop()

            def _add(x, y, z):
                if self.is_wall(x, y, z-1, self.TOP):
                    to = (x, y, z)
                    wp.add_edge_pos(cur, to)
                    if to not in visited:
                        visit.add(to)

            def _check(x, y, z, against):
                if 0 <= x < self.num_x and 0 <= y < self.num_y:
                    if self.is_wall(x, y, z+1, against):
                        return
                    if not self.is_wall(x, y, z, against):
                        if self.is_occupied(x, y, z-1):
                            _add(x, y, z)
                        elif self.is_occupied(x, y, z-2):
                            _add(x, y, z-1)

                    # walk up
                    elif 0 and not self.is_wall(x, y, z+1, against):
                        if self.is_wall(x, y, z, self.TOP):
                            _add(x, y, z+1)

            def _check_diag(xo, yo, z, against):
                if 0 <= x+xo < self.num_x and 0 <= y+yo < self.num_y:
                    if self.is_wall(x+xo, y+yo, z, against) or (
                            self.is_wall(x+xo, y, z, against) or self.is_wall(x, y+yo, z, against)):
                        return
                    if self.is_wall(x+xo, y+yo, z+1, against) or (
                            self.is_wall(x+xo, y, z+1, against) or self.is_wall(x, y+yo, z+1, against)):
                        return
                    if self.is_occupied(x+xo, y+yo, z-1):
                        _add(x+xo, y+yo, z)
                    elif self.is_occupied(x+xo, y+yo, z-2):
                        _add(x+xo, y+yo, z-1)

            x, y, z = cur
            _check(x-1, y, z, self.RIGHT)
            _check(x+1, y, z, self.LEFT)
            _check(x, y-1, z, self.BACK)
            _check(x, y+1, z, self.FRONT)

            _check_diag(-1, -1, z, self.RIGHT | self.BACK)
            _check_diag(+1, -1, z, self.LEFT | self.BACK)
            _check_diag(+1, +1, z, self.LEFT | self.FRONT)
            _check_diag(-1, +1, z, self.RIGHT | self.FRONT)

            visited.add(cur)

        print("waypoints", wp.num_nodes, wp.num_edges)
        return wp
