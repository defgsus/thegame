from .base import PostProcNode


class Add(PostProcNode):

    def __init__(
            self,
            mode: str = "add",
            count: int = 2,
            name: str = "add",
    ):
        super().__init__(name)
        assert count in (1, 2, 3, 4)
        self._mode = mode
        self._count = count

    def get_code(self):
        init_lines, add_lines = [], []
        for i in range(1, self._count + 1):
            init_lines.append(
                f"vec4 col{i} = texture(u_tex{i}, texCoord);"
            )
            add_lines.append(
                f"col0 = add_function(col{i-1}, col{i});"
            )

        if self._mode == "add":
            add_code = """
                return a + b;
            """
        elif self._mode == "mix":
            add_code = """
                return vec4(mix(a.xyz, b.xyz, b.w), max(a.w, b.w));
            """
        else:
            raise ValueError(f"Invalid mode '{self._mode}'")

        code = """        
        vec4 add_function(in vec4 a, in vec4 b) {
            %(add_code)s
        }
        
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            %(init_lines)s
            
            vec4 col0 = vec4(0, 0, 0, 0);
            
            %(add_lines)s
            
            fragColor = clamp(col0, 0, 1);
        }   
        """ % {
            "init_lines": "\n".join(init_lines),
            "add_lines": "\n".join(add_lines),
            "add_code": add_code,
        }
        return code
