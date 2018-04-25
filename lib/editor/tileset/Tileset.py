from PyQt5.QtGui import QImage, QColor


class Tileset:

    def __init__(self, tile_width, tile_height, num_x=0, num_y=0):
        self.tile_width = 0
        self.tile_height = 0
        self.num_tiles_x = 0
        self.num_tiles_y = 0
        self.num_tiles = 0
        self.filename = None
        self.color_qimage = None
        self.height_qimage = None
        self._id_to_pos = dict()
        self._pos_to_id = dict()
        self.color_qimage = None
        self.height_qimage = None
        if num_x and num_y:
            self.init(tile_width, tile_height, num_x, num_y)

    def __str__(self):
        return "Tileset(%sx%s, num=%sx%s=%s)" % (
            self.tile_width, self.tile_height,
            self.num_tiles_x, self.num_tiles_y, self.num_tiles
        )

    def __repr__(self):
        return self.__str__()

    @property
    def image_width(self):
        return self.num_tiles_x * self.tile_width

    @property
    def image_height(self):
        return self.num_tiles_y * self.tile_height

    def init(self, tile_width, tile_height, num_x, num_y):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.num_tiles_x = num_x
        self.num_tiles_y = num_y
        self.num_tiles = self.num_tiles_x * self.num_tiles_y

        # create id/pos mapping
        self._id_to_pos.clear()
        self._pos_to_id.clear()
        k = 1
        for y in range(self.num_tiles_y):
            for x in range(self.num_tiles_x):
                p = (x, y)
                self._id_to_pos[k] = p
                self._pos_to_id[p] = k
                k += 1

        self.color_qimage = QImage(self.image_width, self.image_height, QImage.Format_RGBA8888)
        self.height_qimage = QImage(self.image_width, self.image_height, QImage.Format_RGBA8888)
        self.color_qimage.fill(QColor(255,255,255,0))
        self.height_qimage.fill(QColor(255,255,255,0))

    def load_image(self, filename):
        img = QImage(filename)
        assert img.width() / self.tile_width == img.width() // self.tile_width
        assert img.height() / self.tile_height == img.height() // self.tile_height
        self.init(self.tile_width, self.tile_height,
                  img.width() // self.tile_width, img.height() // self.tile_height)
        self.color_qimage = img
