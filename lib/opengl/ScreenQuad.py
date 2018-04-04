from .Drawable import *
import glm


class ScreenQuad:

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
    uniform sampler2D u_tex1;
    uniform vec4 u_resolution;
    
    in vec4 v_pos;
    in vec2 v_texcoord;
    
    out vec4 fragColor;
    
    void main() {
        vec2 fac = u_resolution.xy/4.;
        vec2 texcoord = floor(v_texcoord*fac) / fac;
        fragColor = texture(u_tex1, texcoord);
        //fragColor += 0.01 * u_resolution;
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