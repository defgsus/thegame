from .base import PostProcNode


class Bypass(PostProcNode):

    def __init__(self, name, alpha=None):
        super().__init__(name)
        self.alpha = alpha

    def get_code(self):
        return """
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            fragColor = texture(u_tex1, texCoord);
            #if %(override)s
                fragColor.w = %(alpha)s;
            #endif
        }   
        """ % {
            "override": 0 if self.alpha is None else 1,
            "alpha": self.alpha,
        }

