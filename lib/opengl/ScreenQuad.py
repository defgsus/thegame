import glm

from . import DEFAULT_SHADER_VERSION
from .Drawable import *


class ScreenQuad:
    """
    Helper to render a quad on screen with custom shader
    """

    VERTEX_SRC = DEFAULT_SHADER_VERSION + """
    #line 13
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

    FRAGMENT_SRC = DEFAULT_SHADER_VERSION + """
    #line 32
    uniform sampler2D u_tex1;
    uniform sampler2D u_tex2;
    uniform sampler2D u_tex3;
    uniform sampler2D u_tex4;
    uniform vec4 u_resolution;
    uniform float u_time;
    
    in vec4 v_pos;
    in vec2 v_texcoord;
    
    out vec4 o_color;
    
    %(mainImage)s

    void main() {
        vec2 _tec = (v_pos.xy*.5+.5);
        vec2 _scr = _tec * u_resolution.xy;
        mainImage(o_color, _scr, v_texcoord);
    }
    """

    DEFAULT_MAIN_IMAGE = """
    #line 50
    void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
        fragColor = texture(u_tex1, texCoord);
        //fragColor = vec4(texCoord, 0, 1);
    }
    """

    def __init__(self, name=None):
        self.name = name or "screenquad"
        self.drawable = Drawable(name=self.name)
        self.drawable.shader.set_fragment_source(self.FRAGMENT_SRC % {"mainImage": self.DEFAULT_MAIN_IMAGE})
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

    def set_shader_code(self, code):
        self.drawable.shader.set_fragment_source(self.FRAGMENT_SRC % {"mainImage": code})

    def release(self):
        self.drawable.release()

    def draw(self, width, height):
        #print("quaddraw", width, height)
        proj = glm.mat4(1.)
        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.shader.set_uniform("u_resolution", (width, height, 1./max(1, width), 1./max(1, height)))
        self.drawable.draw()

    def draw_centered(self, width, height, tex_width, tex_height):
        #print("quaddraw_centered", width, height, tex_width, tex_height)
        if height < width:
            proj = glm.scale(glm.mat4(1), glm.vec3(height/width, 1, 1))
        else:
            proj = glm.scale(glm.mat4(1), glm.vec3(1, width/height, 1))
        if tex_height < tex_width:
            proj = glm.scale(proj, glm.vec3(tex_width/tex_height, 1, 1))
        else:
            proj = glm.scale(proj, glm.vec3(1, tex_height/tex_width, 1))

        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.shader.set_uniform("u_resolution", (tex_width, tex_height, 1./max(1, tex_width), 1./max(1, tex_height)))
        self.drawable.draw()
