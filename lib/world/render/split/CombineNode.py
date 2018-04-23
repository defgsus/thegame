from lib.opengl.postproc import *


class CombineNode(PostProcNode):

    def get_code(self):
        return """
        #line 8
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            vec3 c1 = texture(u_tex1, texCoord).xyz;
            vec3 c2 = texture(u_tex2, texCoord).xyz;
            //vec3 col = texCoord.x < .3 ? c1 : texCoord.x < .7 ? c1 * c2 : c2;
            //vec3 col = c1 * c2; 
            vec3 col = texCoord.x < .5 ? c1 : c2;
            fragColor = vec4(col, 1);
        }
        """

    #def update_uniforms(self, shader, rs, pass_num):
    #    shader.set_uniform("u_time", rs.time)
    #    shader.set_uniform("u_tex1", 0)
    #    shader.set_uniform("u_tex2", 1)