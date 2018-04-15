from .base import PostProcBase


class Wave(PostProcBase):

    def get_code(self):
        return """
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            vec2 uv = fragCoord / u_resolution.xy * 2. - 1.;
            float amt = 1. - max(abs(uv.x), abs(uv.y));
        
            vec2 ofs = sin(vec2(1, 1.1) * u_time + texCoord * 5.) * .1 * amt;
            
            fragColor = texture(u_tex1, texCoord + ofs);
        }   
        """

