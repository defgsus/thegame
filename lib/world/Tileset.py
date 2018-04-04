

class Tileset:
    def __init__(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.width = 0
        self.height = 0
        self.num_tiles = 0
        self.image = None

    def __str__(self):
        return "Tileset(%sx%s, %sx%s)" % (
            self.tile_width, self.tile_height,
            self.width, self.height,
        )

    def __repr__(self):
        return self.__str__()

    def load(self, file):
        from PIL import Image
        self.image = Image.open(file)
        self.width = self.image.width // self.tile_width
        self.height = self.image.height // self.tile_height
        self.num_tiles = self.width * self.height

    def get_uv_quad(self, idx):
        x = idx % self.width
        y = idx // self.width
        return (
            (x / self.width, y / self.height),
            ((x+1) / self.width, y / self.height),
            ((x+1) / self.width, (y+1) / self.height),
            (x / self.width, (y+1) / self.height),
        )
