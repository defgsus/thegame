from .base import PostProcBase


class Pixelize(PostProcBase):

    def get_code(self):
        return """
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            const int NUMX = 2;
            const int NUMY = 2;
            vec2 fac = vec2(NUMX, NUMY);
            vec2 texcoord = floor(fragCoord/fac) * fac;
            fragColor = vec4(0);
            for (int y=0; y<NUMY; ++y)
            for (int x=0; x<NUMX; ++x)
            {
                fragColor += texture(u_tex1, (texcoord + vec2(x, y) / fac) / u_resolution.xy);
            }
            fragColor /= float(NUMX*NUMY);
            
            //fragColor = floor(fragColor*30.)/30.;
        }   
        """

