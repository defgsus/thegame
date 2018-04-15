from .base import PostProcBase


class Blur(PostProcBase):

    def __init__(self, size=10, sigma=.7, dir=(1, 0)):
        """
        :param size: Radius of the blur kernel i
        :param sigma: A modifier to adjust the amount of blur, range is about [0, 1]
        """
        super().__init__()
        self.size = size
        self.sigma = sigma
        self.dir = dir
        self.num_samples = 10

    def update_uniforms(self, shader):
        shader.set_uniform("u_size_sigma", (self.size, self.sigma))
        shader.set_uniform("u_direction",  (self.dir[0]/self.width, self.dir[1]/self.height))

    def get_code(self):
        return """
        #line 22
        uniform vec2        u_size_sigma;   // size, smoothness
        uniform vec2        u_direction;    // (1,0) or (0,1)

        /* http://callumhay.blogspot.de/2010/09/gaussian-blur-shader-glsl.html */
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) 
        {
            float sigma = u_size_sigma.y,
                  size = u_size_sigma.x,
                  sum = 0.;
        
            vec3 inc;
            inc.x = 1. / (sqrt(3.14159265*2.) * sigma);
            inc.y = exp(-.5 / (sigma * sigma));
            inc.z = inc.y * inc.y;
        
            vec4 c = texture(u_tex1, texCoord) * inc.x;
            sum += inc.x;
            inc.xy *= inc.yz;
        
            vec2 stp = u_direction * size;
            for (float i=1.; i<%(num)s; ++i)
            {
                c += texture(u_tex1, texCoord + stp * i) * inc.x;
                c += texture(u_tex1, texCoord - stp * i) * inc.x;
                sum += 2. * inc.x;
                inc.xy *= inc.yz;
            }
        
            c /= sum;
        
            fragColor = clamp(vec4(c.xyz, 1.), 0., 1.);
        }

        """ % {
            "num": self.num_samples,
        }

