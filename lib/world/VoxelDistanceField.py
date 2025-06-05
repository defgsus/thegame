import math, json
import glm
from pyglet.gl import *
from lib.opengl import Texture3D


class VoxelDistanceField:

    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth
        self.values = [0] * (width * height * depth)
        self.distances = [0.] * (width * height * depth)

    def save_json(self, filename):
        with open(filename, "w") as fp:
            json.dump({
                "w": self.width,
                "h": self.height,
                "d": self.depth,
                "values": self.values,
                "distances": self.distances }, fp)

    def load_json(self, filename):
        with open(filename) as fp:
            obj = json.load(fp)
            self.width = obj["w"]
            self.height = obj["h"]
            self.depth = obj["d"]
            self.values = obj["values"]
            self.distances = obj["distances"]

    def size(self):
        return (self.width, self.height, self.depth)

    def pos_to_index(self, x, y, z):
        return (z*self.height+y)*self.width+x

    def value(self, x, y, z):
        if not (0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.depth):
            return 0
        return self.values[self.pos_to_index(x, y, z)]

    def set_value(self, x, y, z, val):
        self.values[self.pos_to_index(x, y, z)] = val

    def calc_distances_exact_superslow(self, max_range=None):
        if max_range is None:
            max_range = max(self.size())
        mask = []
        for z in range(-max_range, max_range+1):
            #print("%s/%s" % (z, max_range*2+1))
            for y in range(-max_range, max_range+1):
                for x in range(-max_range, max_range+1):
                    mask.append((x,y,z, glm.length((x,y,z))))
        mask = sorted(mask, key=lambda m: m[3])
        mask = mask[1:]
        max_dist = mask[-1][3]

        for z in range(self.depth):
            print("%s/%s" % (z, self.depth))
            for y in range(self.height):
                #print("%s/%s/%s" % (z, y, self.height))
                for x in range(self.width):
                    if self.value(x, y, z):
                        mindist = 0
                    else:
                        mindist = max_dist
                        for m in mask:
                            if self.value(x+m[0], y+m[1], z+m[2]):
                                d = m[3]
                                #print(m[0], m[1], m[2], d)
                                if d > mindist:
                                    break
                                mindist = d
                            if mindist < 1:
                                break
                        #print("------", mindist)
                    self.distances[self.pos_to_index(x, y, z)] = mindist

    def calc_distances(self):
        """'Dead Reckoning' signed distance field"""
        max_dist = math.sqrt(self.width*self.width+self.height*self.height+self.depth*self.depth)
        self.distances = []
        coords = []

        # init and detect border
        diff = 0.01
        for z in range(self.depth):
            for y in range(self.height):
                for x in range(self.width):
                    val = self.value(x, y, z)
                    dist = max_dist
                    pos = (0,0,0)
                    if (x > 0 and (val - self.value(x-1, y, z)) >= diff) \
                    or (y > 0 and (val - self.value(x, y-1, z)) >= diff) \
                    or (z > 0 and (val - self.value(x, y, z-1)) >= diff):
                    #or (x < self.width-1 and (self.value(x+1, y, z) - val) >= diff) \
                    #or (y < self.height-1 and (self.value(x, y+1, z) - val) >= diff) \
                    #or (z < self.depth-1 and (self.value(x, y, z+1) - val) >= diff):
                        dist = 0.
                        pos = (x, y, z)
                    self.distances.append(dist)
                    coords.append(pos)

        def _test(xo, yo, zo):
            if 0 <= x+xo < self.width and 0 <= y+yo < self.height and 0 <= z+zo < self.depth:
                other_idx = self.pos_to_index(x+xo, y+yo, z+zo)
                if self.distances[other_idx] + math.sqrt(xo*xo+yo*yo+zo*zo) < cur_dist:
                    c = coords[other_idx]
                    coords[idx] = c
                    self.distances[idx] = math.sqrt((x-c[0])*(x-c[0]) + (y-c[1])*(y-c[1]) + (z-c[2])*(z-c[2]))
                    #if self.distances[idx] == 0.:
                    #    print(x,y,z,"|",*c,"=",self.distances[idx])
                    return 1
            return 0

        # iterate until finished
        prev_num_changed1, prev_num_changed2 = -1, -1
        iter, num_iters = 0, 10
        while iter < num_iters:
            print("sdf iter %s/%s" % (iter, num_iters))
            num_changed = 0

            # forward pass
            for z in range(self.depth):
                for y in range(self.height):
                    for x in range(self.width):
                        idx = self.pos_to_index(x, y, z)
                        cur_dist = self.distances[idx]
                        num_changed += _test(-1, -1, -1)
                        num_changed += _test(-1, -1, -1)
                        num_changed += _test( 0, -1, -1)
                        num_changed += _test(+1, -1, -1)
                        num_changed += _test(-1,  0, -1)
                        num_changed += _test(+1,  0, -1)
                        num_changed += _test(-1, +1, -1)
                        num_changed += _test( 0, +1, -1)
                        num_changed += _test(+1, +1, -1)
            
                        num_changed += _test(-1, -1,  0)
                        num_changed += _test( 0, -1,  0)
                        num_changed += _test(+1, -1,  0)
                        num_changed += _test(-1,  0,  0)
            
                        num_changed += _test(-1, -1, +1)

            # backward pass
            for z in range(self.depth):
                for y in range(self.height):
                    for x in range(self.width):
                        idx = self.pos_to_index(x, y, z)
                        cur_dist = self.distances[idx]

                        num_changed += _test(+1, +1, -1)
            
                        num_changed += _test(+1,  0,  0)
                        num_changed += _test(-1, +1,  0)
                        num_changed += _test( 0, +1,  0)
                        num_changed += _test(+1, +1,  0)
            
                        num_changed += _test(-1, -1, +1)
                        num_changed += _test( 0, -1, +1)
                        num_changed += _test(+1, -1, +1)
                        num_changed += _test(-1,  0, +1)
                        num_changed += _test(+1,  0, +1)
                        num_changed += _test(-1, +1, +1)
                        num_changed += _test( 0, +1, +1)
                        num_changed += _test(+1, +1, +1)

            if num_changed == prev_num_changed2:
                break
            prev_num_changed2 = prev_num_changed1
            prev_num_changed1 = num_changed

            if iter > num_iters * 3 // 4:
                num_iters += 10
            iter += 1

        # set sign
        for i, v in enumerate(self.values):
            if v > 0.:
                self.distances[i] *= -1.

    def create_texture3d(self, name=None):
        tex = Texture3D(name=name)
        tex.wrap_mode = GL_CLAMP_TO_EDGE
        tex.mag_filter = GL_LINEAR
        tex.create()
        tex.bind()
        print("MAX", max(self.distances))
        tex.upload(self.distances, self.width, self.height, self.depth,
                   input_format=GL_RED)
        return tex


if __name__ == "__main__":

    df = VoxelDistanceField(10, 10, 2)
    df.set_value(5, 5, 1, 1)
    if 0:
        for x in range(10):
            for y in range(10):
                df.set_value(x, y, 0, 1)
    df.calc_distances_exact_superslow()
    dist_exact = df.distances
    df.calc_distances()
    dist_dr = df.distances
    for i in range(df.depth*10):
        if i % 10 == 0:
            print("-"*50)
        s1 = " ".join("%4s" % round(x, 2) for x in dist_exact[i*10:(i+1)*10])
        s2 = " ".join("%4s" % round(x, 2) for x in dist_dr[i*10:(i+1)*10])
        print("%s  |  %s" % (s1, s2))