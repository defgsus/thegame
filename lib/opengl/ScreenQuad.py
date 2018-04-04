from .Drawable import *
import glm


class ScreenQuad:
    """
    Helper to render a quad on screen with custom shader
    TODO: currently not custom
    """

    VERTEX_SRC = """
    #version 130
    uniform mat4 u_projection;
    uniform vec4 u_resolution;
    
    in vec4 a_position;
    in vec2 a_texcoord;
    
    out vec4 v_pos;
    out vec2 v_texcoord;
    
    void main()
    {
        v_pos = a_position;
        v_texcoord = a_texcoord;
        gl_Position = u_projection * a_position;
    }
    """

    FRAGMENT_SRC = """
    #version 130
    #line 28
    uniform sampler2D u_tex1;
    uniform vec4 u_resolution;
    
    in vec4 v_pos;
    in vec2 v_texcoord;
    
    out vec4 o_color;
    
    void mainImage(out vec4 fragColor, in vec2 fragCoord) {
        const int NUMX = 3;
        const int NUMY = 3;
        vec2 fac = vec2(NUMX, NUMY);
        vec2 texcoord = floor(fragCoord/fac) * fac;
        fragColor = vec4(0);
        for (int y=0; y<NUMY; ++y)
        for (int x=0; x<NUMX; ++x)
        {
            fragColor += texture(u_tex1, (texcoord + vec2(x, y) / fac) / u_resolution.xy);
        }
        fragColor /= float(NUMX*NUMY);
    }
    
    void main() {
        vec2 scr = (v_pos.xy*.5+.5) * u_resolution.xy;
        mainImage(o_color, scr);
    }
    """

    def __init__(self):
        self.drawable = Drawable()
        self.drawable.shader.set_fragment_source(self.FRAGMENT_SRC)
        self.drawable.shader.set_vertex_source(self.VERTEX_SRC)
        self.drawable.set_attribute(
            "a_position", 2,
            [-1,-1,  1,-1,  1,1,  -1,1],
        )
        self.drawable.set_attribute(
            "a_texcoord", 2,
            [0, 0,  1, 0,  1, 1,  0, 1],
        )
        self.drawable.set_index(
            GL_TRIANGLES,
            [0,1,2, 0,2,3]
        )

    def release(self):
        self.drawable.release()

    def draw(self, width, height):
        proj = glm.mat4(1.)
        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.shader.set_uniform("u_resolution", (width, height, 1./max(1, width), 1./max(1, height)))
        self.drawable.draw()