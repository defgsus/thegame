import pyglet
import glm
from pyglet.gl import *
from lib.opengl.VertexArrayObject import *
from lib.opengl.Shader import *
from lib.opengl.Drawable import Drawable
from lib.geom.TriangleMesh import TriangleHashMesh, TriangleMesh

frag_src = """#version 130

in vec4 v_pos;
in vec3 v_normal;

out vec4 fragColor;

vec3 poscol(in vec4 p) {
    float z = p.z*4.;
    return vec3(1.-z, .3+z, 0.);
}

void main() {
    vec2 grid = mod(v_pos.xy*10., 1.);
    vec3 col = vec3(0);
    float g = smoothstep(.02, .0, .49-abs(grid.x-.5));
    g = max(g, smoothstep(.02, .0, .49-abs(grid.y-.5)));
    col += 1.-g;
    col = mix(col, poscol(v_pos), .4);
    col = mix(col, v_normal*.5+.5, .5); 
    fragColor = vec4(col, 1);
}
"""

HEIGHTMAP = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 1, 2, 2, 2, 2, 2, 0, 0],
    [0, 0, 1, 2, 1, 1, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

class OrthoWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(OrthoWindow, self).__init__(*args, **kwargs)
        self.mesh = TriangleMesh()
        #self.mesh = TriangleHashMesh()
        import random
        def heightmap(x, y):
            return HEIGHTMAP[max(0,min(9,y))][max(0,min(9,x))] / 10
            #return random.randrange(max(1,random.randrange(3)))/10
        self.mesh.create_height_map(10,10, heightmap, 1./10)
        self.drawable = self.mesh.get_drawable()
        self.drawable.shader.set_fragment_source(frag_src)

        self.projection = "i"
        self._init_rotation()

    def on_draw(self):
        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        self.clear()

        if self.projection in "io":
            proj = glm.ortho(-.5,.5, .5,-.5, -2, 2)
        else:
            proj = glm.perspective(30., self.width / self.height, 0.01, 10.)
            proj = glm.translate(proj, (0,0,-1))
        proj = glm.rotate(proj, self.rotate_x, (1,0,0))
        proj = glm.rotate(proj, self.rotate_y, (0,1,0))
        proj = glm.rotate(proj, self.rotate_z, (0,0,1))
        #print(proj)

        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.draw()
        #OpenGlBaseObject.dump_instances()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.rotate_x += scroll_y / 30.

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.rotate_y += dx / 30.

    def on_text(self, text):
        if text == "o":
            self.projection = "o"
            self._init_rotation()
        if text == "i":
            self.projection = "i"
            self._init_rotation()
            self.rotate_z = glm.pi()/4
        if text == "p":
            self.projection = "p"
            self._init_rotation()

    def _init_rotation(self):
        self.rotate_x = glm.pi()/(3.3 if self.projection=="i" else 4)
        self.rotate_y = 0#-glm.pi()/4.
        self.rotate_z = 0