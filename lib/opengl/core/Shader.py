import re
from pathlib import Path
from typing import Optional

from .base import *


class ShaderUniform:
    def __init__(self, name: str, type, size, location):
        self.name = name
        self.type = type
        self.size = size
        self.location = location


class Shader(OpenGlBaseObject):

    DEFAULT_INCLUDE_PATH: Path = Path(__file__).resolve().parent.parent / "shaders"

    _RE_INCLUDE = re.compile(r"^\s*#include\s*<([^>]+)>\s*$")
    _RE_LINE = re.compile(r"^\s*#line\s*(\d+)\s*$")
    _RE_LOG_ERROR = re.compile(".*\((\d+)\) : error (.*)", re.MULTILINE)

    def __init__(
            self,
            vertex_source: Optional[str] = None,
            fragment_source: Optional[str] = None,
            name: str = None
    ):
        super(Shader, self).__init__(name=name)
        self._vertex_source = vertex_source
        self._fragment_source = fragment_source
        self._log = ""
        self._uniforms = dict()
        self._attributes = dict()
        self._uniform_values = dict()
        self._shaders = []
        self._source_changed = True
        self._is_compiled = False

    def is_compiled(self) -> bool:
        return self._is_compiled

    def is_source_changed(self) -> bool:
        return self._source_changed

    def has_uniform(self, name: str) -> bool:
        return name in self._uniforms

    def has_attribute(self, name: str) -> bool:
        return name in self._attributes

    def uniform(self, name: str) -> ShaderUniform:
        if name not in self._uniforms:
            raise KeyError("uniform '%s' not found, possible values: %s" % (name, self.dump_variables(do_print=False)))
        return self._uniforms[name]

    def attribute(self, name) -> ShaderUniform:
        if name not in self._attributes:
            raise KeyError("attribute '%s' not found, possible values: %s" % (name, self.dump_variables(do_print=False)))
        return self._attributes[name]

    @property
    def vertex_source(self) -> Optional[str]:
        return self._vertex_source

    @property
    def fragment_source(self) -> Optional[str]:
        return self._fragment_source

    def set_vertex_source(self, src: str):
        src = self._add_includes(src)
        self._source_changed = src != self._vertex_source
        self._vertex_source = src

    def set_fragment_source(self, src: str):
        src = self._add_includes(src)
        self._source_changed = src != self._fragment_source
        self._fragment_source = src

    def set_uniform(self, name: str, value):
        self._uniform_values[name] = value

    def update_uniforms(self):
        for name in self._uniform_values:
            if name in self._uniforms:
                value = self._uniform_values[name]
                u = self.uniform(name)
                if u.type in (GL_INT, GL_SAMPLER_1D, GL_SAMPLER_2D, GL_SAMPLER_3D):
                    glUniform1i(u.location, value)

                elif u.type == GL_INT_VEC2:
                    glUniform2i(u.location, value[0], value[1])
                elif u.type == GL_INT_VEC3:
                    glUniform3i(u.location, value[0], value[1], value[2])
                elif u.type == GL_INT_VEC4:
                    glUniform4i(u.location, value[0], value[1], value[2], value[3])

                elif u.type == GL_FLOAT:
                    glUniform1f(u.location, value)
                elif u.type == GL_FLOAT_VEC2:
                    glUniform2f(u.location, value[0], value[1])
                elif u.type == GL_FLOAT_VEC3:
                    glUniform3f(u.location, value[0], value[1], value[2])
                elif u.type == GL_FLOAT_VEC4:
                    glUniform4f(u.location, value[0], value[1], value[2], value[3])

                elif u.type == GL_FLOAT_MAT3:
                    value = sum((list(i) for i in value), [])
                    v = (GLfloat * len(value))(*value)
                    glUniformMatrix3fv(u.location, 1, GL_FALSE, v)
                elif u.type == GL_FLOAT_MAT4:
                    value = sum((list(i) for i in value), [])
                    v = (GLfloat * len(value))(*value)
                    glUniformMatrix4fv(u.location, 1, GL_FALSE, v)
                else:
                    raise ValueError("Unsupported type enum %s for uniform %s" % (u.type, u.name))
        self._uniform_values.clear()

    def _create(self):
        self._handle = glCreateProgram()

    def _release(self):
        self._release_shaders()
        self._is_compiled = False
        glDeleteProgram(self._handle)

    def _bind(self):
        glUseProgram(self._handle)

    def _unbind(self):
        glUseProgram(0)

    def _release_shaders(self):
        for s in self._shaders:
            glDeleteShader(s)
        self._shaders.clear()

    def compile(self):
        self.check_created("compile")
        self._release_shaders()
        self._compile_shader(GL_VERTEX_SHADER, "vertex shader", self._vertex_source)
        self._compile_shader(GL_FRAGMENT_SHADER, "fragment shader", self._fragment_source)
        glLinkProgram(self._handle)
        self._source_changed = False
        self._is_compiled = True

        loglen = GLint(0)
        glGetProgramiv(self._handle, GL_INFO_LOG_LENGTH, ctypes.byref(loglen))
        infolog = ctypes.create_string_buffer(loglen.value)
        glGetProgramInfoLog(self._handle, loglen, None, infolog)
        self._log += infolog.value.decode("utf-8") + "\n"

        self._log = self._log.strip()
        if self._log:
            print(self._log)

        self._get_uniforms()
        self._get_attributes()

    def _compile_shader(self, shader_type, shader_type_name, source):
        shader = glCreateShader(shader_type)
        psrc = (ctypes.c_char_p * 1)(source.encode("utf-8"))
        psrc = ctypes.cast(ctypes.pointer(psrc), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
        glShaderSource(shader, 1, psrc, None)
        glCompileShader(shader)

        loglen = GLint(0)
        glGetShaderiv(shader, GL_INFO_LOG_LENGTH, ctypes.byref(loglen))
        infolog = ctypes.create_string_buffer(loglen.value)
        glGetShaderInfoLog(shader, loglen, None, infolog)
        self._log += infolog.value.decode("utf-8") + "\n"

        status = GLint(0)
        glGetShaderiv(shader, GL_COMPILE_STATUS, ctypes.byref(status))
        if not status:
            self._log += "\n".join(self._get_error_lines(source, self._log))
            print(self._log)
            raise OpenGlError(
                f"'{self.name}' {shader_type_name} compilation error\n{self._log}"
                # f"\n{source}"
            )

        glAttachShader(self._handle, shader)
        self._shaders.append(shader)

    def _get_error_lines(self, source: str, log: str):
        # TODO: this is messy
        source_lines = dict()
        count = 1
        for line in source.splitlines():
            match = self._RE_LINE.match(line)
            if match:
                count = int(match.groups()[0])
            if count not in source_lines:
                source_lines[count] = []
            source_lines[count].append(line)
            count += 1

        ret_lines = []

        for match in self._RE_LOG_ERROR.finditer(log):
            line_num, message = match.groups()
            line_num = int(line_num)
            ret_lines.append("")
            ret_lines.append(f"{line_num}: {message}")
            for l_idx in range(max(1, line_num - 2), line_num + 2):
                lines = source_lines.get(l_idx)
                if lines:
                    star = ">" if l_idx == line_num else " "
                    for line in lines:
                        ret_lines.append(f"  {star}{l_idx:8}: {line}")
        return ret_lines

    def _get_uniforms(self):
        self._uniforms.clear()
        num_uniforms = GLint(0)
        glGetProgramiv(self._handle, GL_ACTIVE_UNIFORMS, ctypes.byref(num_uniforms))

        max_name_length = GLint(0)
        glGetProgramiv(self._handle, GL_ACTIVE_UNIFORM_MAX_LENGTH, ctypes.byref(max_name_length))

        for i in range(num_uniforms.value):
            namebuf = ctypes.create_string_buffer(max_name_length.value)
            name_length = GLint(0)
            uniform_size = GLint(0)
            uniform_type = GLenum(0)
            glGetActiveUniform(self._handle, i, max_name_length, ctypes.byref(name_length),
                               ctypes.byref(uniform_size), ctypes.byref(uniform_type), namebuf)
            #print(namebuf.value, uniform_type.value)
            location = glGetUniformLocation(self._handle, namebuf)
            uniform = ShaderUniform(namebuf.value.decode("utf-8"), uniform_type.value, uniform_size.value, location)
            self._uniforms[uniform.name] = uniform

    def _get_attributes(self):
        self._attributes.clear()
        num_attributes = GLint(0)
        glGetProgramiv(self._handle, GL_ACTIVE_ATTRIBUTES, ctypes.byref(num_attributes))

        max_name_length = GLint(0)
        glGetProgramiv(self._handle, GL_ACTIVE_ATTRIBUTE_MAX_LENGTH, ctypes.byref(max_name_length))

        for i in range(num_attributes.value):
            namebuf = ctypes.create_string_buffer(max_name_length.value)
            name_length = GLint(0)
            uniform_size = GLint(0)
            uniform_type = GLenum(0)
            glGetActiveAttrib(self._handle, i, max_name_length, ctypes.byref(name_length),
                               ctypes.byref(uniform_size), ctypes.byref(uniform_type), namebuf)
            location = glGetAttribLocation(self._handle, namebuf)
            attribute = ShaderUniform(namebuf.value.decode("utf-8"), uniform_type.value, uniform_size.value, location)
            self._attributes[attribute.name] = attribute

    def dump_variables(self, do_print: bool = True) -> str:
        s = ""
        for u in list(self._uniforms.values()) + list(self._attributes.values()):
            s += "%3s %6s %2s %s\n" % (u.location, u.type, u.size, u.name)
        if do_print:
            print(s)
        return s

    def get_include_file(self, filename: str) -> Optional[str]:
        if ".." in filename:
            raise ValueError(
                f"Relative paths for includes are certainly not allowed"
                f", got '{filename}' in shader '{self.name}"
            )

        fn = self.DEFAULT_INCLUDE_PATH / filename
        if not fn.exists():
            return None
        return fn.read_text()

    def _add_includes(self, code: str, included_set: Optional[set] = None):
        if included_set is None:
            included_set = set()

        lines = code.splitlines()
        ret_lines = []
        for line in lines:
            include_match = self._RE_INCLUDE.match(line)
            if not include_match:
                ret_lines.append(line)
            else:
                filename = include_match.groups()[0]
                if filename not in included_set:
                    included_set.add(filename)
                    included_code = self.get_include_file(filename)
                    if included_code is None:
                        raise ValueError(f"Shader '{self.name}' could not include '{filename}'")
                    included_code = self._add_includes(included_code, included_set=included_set)
                    ret_lines += included_code.splitlines()

        return "\n".join(ret_lines)
