

class Tileset:

    _loaded_sets = dict()

    @classmethod
    def from_image(cls, tile_width, tile_height, filename) -> "Tileset":
        key = (tile_width, tile_height, filename)
        if key not in cls._loaded_sets:
            ts = Tileset(tile_width, tile_height)
            ts.load(filename)
            cls._loaded_sets[key] = ts
        return cls._loaded_sets[key]

    def __init__(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.width = 0
        self.height = 0
        self.num_tiles = 0
        self.padding = .5/16.
        self.values = None
        self.filename = None

    def __str__(self):
        return "Tileset(%sx%s, %sx%s)" % (
            self.tile_width, self.tile_height,
            self.width, self.height,
        )

    def __repr__(self):
        return self.__str__()

    def load(self, file):
        from PIL import Image
        image = Image.open(file)
        try:
            num_chan = len(image.getpixel((0, 0)))
        except TypeError:
            num_chan = 1
        self.values = image.tobytes("raw")
        if num_chan < 4:
            values = []
            for v in self.values:
                values.append(v)
                for c in range(max(0, 3-num_chan)):
                    values.append(v)
                values.append(255)
            self.values = values
        self.values = [float(v) / 255 for v in self.values]
        self.width = image.width // self.tile_width
        self.height = image.height // self.tile_height
        self.num_tiles = self.width * self.height
        #self.values = self._flip_y(self.values)
        self._create_bumpmaps()
        self.filename = "%s" % file

    def create_texture2d(self, asset_suffix=None):
        from ..opengl import Texture2D
        from ..opengl.core.base import GL_RGBA, GL_FLOAT
        from ..opengl import OpenGlAssets
        texture_name = self.filename
        if asset_suffix is not None:
            texture_name = "%s-%s" % (texture_name, asset_suffix)
        if OpenGlAssets.has(self.filename):
            return OpenGlAssets.get(texture_name)
        else:
            tex = Texture2D(name="tileset")
            tex.create()
            tex.bind()
            tex.upload(self.values, self.width*self.tile_width, self.height*self.tile_height,
                       input_format=GL_RGBA, input_type=GL_FLOAT, do_flip_y=True)
            OpenGlAssets.register(texture_name, tex)
            return tex

    def get_uv_quad(self, idx):
        x = idx % self.width
        y = idx // self.width
        y = self.width - 1 - y
        x1 = x + 1 - self.padding
        y1 = y + 1 - self.padding
        x = x + self.padding
        y = y + self.padding
        return (
            (x  / self.width, y  / self.height),
            (x1 / self.width, y  / self.height),
            (x1 / self.width, y1 / self.height),
            (x  / self.width, y1 / self.height),
        )

    def get_uv_offset(self, idx):
        x = idx % self.width
        y = idx // self.width
        return x / self.width, -y / self.height

    def _flip_y(self, values):
        width = self.width * self.tile_width
        height = self.height * self.tile_height
        num_chan = 4
        ret = []
        for i in range(height, 0, -1):
            ret += values[(i-1)*width*num_chan:i*width*num_chan]
        return ret

    def _create_bumpmaps(self):
        for j in range(6):
            for i in range(self.width//2, self.width):
                self._create_bumpmap(i, j)

    def _create_bumpmap(self, tilex, tiley):
        import glm
        normals = []
        for y in range(self.tile_height):
            for x in range(self.tile_width):
                n = glm.normalize(glm.vec3(
                    self._get_pixel(tilex, tiley, x+1, y) - self._get_pixel(tilex, tiley, x-1, y),
                    self._get_pixel(tilex, tiley, x, y-1) - self._get_pixel(tilex, tiley, x, y+1),
                    .5))
                normals.append(n)

        for y in range(self.tile_height):
            for x in range(self.tile_width):
                ofs = ((tiley*self.tile_height+y) * self.tile_width*self.width + (tilex*self.tile_width) + x)*4
                n = normals[y*self.tile_width+x]
                # keep green as specular map
                self.values[ofs+3] = self.values[ofs+1]
                self.values[ofs] = n[0]
                self.values[ofs+1] = n[1]
                self.values[ofs+2] = n[2]

    def _get_pixel(self, tilex, tiley, x, y):
        if x < 0:
            x += self.tile_width
        elif x >= self.tile_width:
            x -= self.tile_width
        if y < 0:
            y += self.tile_height
        elif y >= self.tile_height:
            y -= self.tile_height
        ofsx = tilex * self.tile_width + x
        ofsy = tiley * self.tile_height + y
        return self.values[(ofsy * self.tile_width * self.width + ofsx)*4]
