from .base import PostProcNode


class Desaturate(PostProcNode):

    def get_code(self):
        return """
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            fragColor = texture(u_tex1, texCoord);
            fragColor.xyz = vec3(dot(fragColor.xyz, vec3(.3,.6,.1)));
        }   
        """

