from .base import PostProcNode


class Wave(PostProcNode):

    def get_code(self):
        return """
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            vec2 uv = fragCoord / u_resolution.xy * 2. - 1.;
            float amt = max(0., 1. - length(uv));
        
            vec2 ofs = sin(vec2(1, 1.1) * u_time + texCoord * 5.) * .1 * amt;
            
            fragColor = texture(u_tex1, texCoord + ofs);
            //fragColor = vec4(vec3(amt), 1);
        }   
        """

