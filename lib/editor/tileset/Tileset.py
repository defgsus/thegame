from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Tileset:

    def __init__(self, tile_width, tile_height, num_x=0, num_y=0):
        self.tile_width = tile_width
        self.tile_height = tile_height
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

    def to_json_data(self):
        """Returns a json-serializable object"""
        return {
            "tile_width": self.tile_width,
            "tile_height": self.tile_height,
            "num_x": self.num_tiles_x,
            "num_y": self.num_tiles_y,
            "ids": self._id_to_pos,
            "png": {
                "color": qimage_to_base64(self.color_qimage),
                "height": qimage_to_base64(self.color_qimage),
            },
        }

    def from_json_data(self, obj):
        """Initializes the data from a json-serializeable object"""
        self.init(obj["tile_width"], obj["tile_height"], obj["num_x"], obj["num_y"])
        self._id_to_pos = {i: tuple(obj["ids"][i]) for i in obj["ids"]}
        self._pos_to_id = {self._id_to_pos[i]: i for i in self._id_to_pos}
        self.color_qimage = base64_to_qimage(obj["png"]["color"])
        self.height_qimage = base64_to_qimage(obj["png"]["height"])

    def save(self, filename):
        import json
        with open(filename, "w") as fp:
            json.dump(self.to_json_data(), fp)
        self.filename = filename

    def load(self, filename):
        import json
        with open(filename) as fp:
            data = json.load(fp)
        self.from_json_data(data)
        self.filename = filename


def qimage_to_base64(qimage):
    io = QBuffer()
    io.open(QBuffer.ReadWrite)
    writer = QImageWriter(io, b"png")
    writer.write(qimage)
    io.seek(0)
    return bytes(io.readAll().toBase64()).decode("ascii")


def base64_to_qimage(coded):
    data = QByteArray.fromBase64(bytes(coded, "ascii"))
    io = QBuffer(data)
    reader = QImageReader(io, b"png")
    img = reader.read()
    return img


if __name__ == "__main__":
    img = QImage(100, 100, QImage.Format_RGBA8888)
    b = qimage_to_base64(img)
    print("[%s|%s]" % (type(b), b))
    img = base64_to_qimage(b)
    print(img, img.width(), img.height())
    b2 = qimage_to_base64(img)
    assert b == b2
