from .Drawable import Drawable


class CoordinateGrid:
    def __init__(self):
        self.drawable = Drawable()

    def release(self):
        self.drawable.release()
