from .base import PostProcNode


class Blur(PostProcNode):

    def __init__(self, name, size=2, sigma=.7, num_samples=10,
                 use_mask=False, mask_center=0.25, mask_spread=0.1,
                 num_passes=1):
        """
        :param size: Radius of the blur kernel - tied to resolution
        :param sigma: A modifier to adjust the amount of blur, range is about [0, 1]
        """
        super().__init__(name)
        self.size = size
        self.sigma = sigma
        self._num_samples = num_samples
        self._use_mask = use_mask
        self.mask_center = mask_center
        self.mask_spread = mask_spread
        self._num_passes = num_passes

    def num_passes(self):
        return 2 * self._num_passes

    @property
    def num_samples(self):
        return self._num_samples

    @num_samples.setter
    def num_samples(self, num):
        if self._num_samples != num:
            self.do_compile = True
        self._num_samples = num

    @property
    def use_mask(self):
        return self._use_mask

    @use_mask.setter
    def use_mask(self, bool):
        if self._use_mask != bool:
            self.do_compile = True
        self._use_mask = bool

    def update_uniforms(self, shader, rs, pass_num):
        dir = [(1, 0), (0,1)][pass_num%2]
        shader.set_uniform("u_size_sigma", (self.size * rs.render_width / 600.,
                                            self.sigma * self.num_samples * .5))
        shader.set_uniform("u_direction",  (dir[0]/rs.render_width, dir[1]/rs.render_height))
        shader.set_uniform("u_mask_center_spread", (self.mask_center, self.mask_spread))

    def get_code(self):
        return """
        #line 22
        uniform vec2        u_size_sigma;   // size, smoothness
        uniform vec2        u_direction;    // (1,0) or (0,1)
        uniform vec2        u_mask_center_spread;

        /* http://callumhay.blogspot.de/2010/09/gaussian-blur-shader-glsl.html */
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) 
        {
            float sigma = u_size_sigma.y,
                  size = u_size_sigma.x,
                  sum = 0.;
        
        #if %(mask)s
            sigma = max(0.001,
                sigma * (1.-smoothstep(u_mask_center_spread.y, 0., abs(texture(u_tex2, texCoord).x - u_mask_center_spread.x)))
                );
        #endif

            vec3 inc;
            inc.x = 1. / (sqrt(3.14159265*2.) * sigma);
            inc.y = exp(-.5 / (sigma * sigma));
            inc.z = inc.y * inc.y;
        
            vec4 c = texture(u_tex1, texCoord) * inc.x;
            sum += inc.x;
            inc.xy *= inc.yz;
        
            vec2 stp = u_direction * size;
            for (float i=1.; i<float(%(num)s); ++i)
            {
                c += texture(u_tex1, texCoord + stp * i) * inc.x;
                c += texture(u_tex1, texCoord - stp * i) * inc.x;
                sum += 2. * inc.x;
                inc.xy *= inc.yz;
            }
        
            c /= sum;
        
            fragColor = clamp(vec4(c.xyz, 1.), 0., 1.);
            
            /*float D = texture(u_tex2, texCoord).x;
            float e = smoothstep(0.001, .0, abs(D-.999));
            fragColor += vec4(D,e,e,1);*/
        }

        """ % {
            "num": self.num_samples,
            "mask": 1 if self.use_mask else 0,
        }

