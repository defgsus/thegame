from .Drawable import Drawable
from ..geom import LineMesh

FRAGMENT_SRC = """
#version 130

in vec4 v_pos;
in vec4 v_color;

out vec4 fragColor;

void main() {
    fragColor = v_color;
}
"""

class CoordinateGrid:
    def __init__(self, size=20):
        self.drawable = Drawable()

        mesh = LineMesh()
        mesh.set_color(1, 0, 0)
        for i in range(size):
            mesh.add_line((i, 0, 0), (i+1, 0, 0))
            mesh.add_line((i, -.2, 0), (i, .2, 0))

        mesh.set_color(0, 1, 0)
        for i in range(size):
            mesh.add_line((0, i, 0), (0, i+1, 0))
            mesh.add_line((-.2, i, 0), (.2, i, 0))

        mesh.set_color(0, 1, 1)
        for i in range(size):
            mesh.add_line((0, 0, i), (0, 0, i+1))
            mesh.add_line((-.2, 0, i), (.2, 0, i))

        self.drawable = mesh.create_drawable()
        self.drawable.shader.set_fragment_source(FRAGMENT_SRC)

    def release(self):
        self.drawable.release()

    def draw(self):
        self.drawable.draw()
