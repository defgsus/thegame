import ctypes
from .base import *


class ShaderUniform:
    def __init__(self, name, type, size, location):
        self.name = name
        self.type = type
        self.size = size
        self.location = location


class Shader(OpenGlBaseObject):

    def __init__(self, vertex_source, fragment_source, name=None):
        super(Shader, self).__init__(name=name)
        self._vertex_source = vertex_source
        self._fragment_source = fragment_source
        self._log = ""
        self._uniforms = dict()
        self._attributes = dict()

    def uniform(self, name):
        return self._uniforms.get(name)

    def attribute(self, name):
        return self._attributes.get(name)

    def _create(self):
        self._handle = glCreateProgram()

    def _release(self):
        glDeleteProgram(self._handle)

    def _bind(self):
        glUseProgram(self._handle)

    def _unbind(self):
        glUseProgram(0)

    def compile(self):
        self.check_created("compile")
        self._compile_shader(GL_VERTEX_SHADER, "vertex shader", self._vertex_source)
        self._compile_shader(GL_FRAGMENT_SHADER, "fragment shader", self._fragment_source)
        glLinkProgram(self._handle)

        loglen = GLint(0)
        glGetProgramiv(self._handle, GL_INFO_LOG_LENGTH, ctypes.byref(loglen))
        infolog = ctypes.create_string_buffer(loglen.value)
        glGetProgramInfoLog(self._handle, loglen, None, infolog)
        self._log += infolog.value.decode("utf-8") + "\n"

        print(self._log.strip())

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

        glAttachShader(self._handle, shader)

    def _get_uniforms(self):
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
            location = glGetUniformLocation(self._handle, namebuf)
            uniform = ShaderUniform(namebuf.value.decode("utf-8"), uniform_size.value, uniform_type.value, location)
            self._uniforms[uniform.name] = uniform

    def _get_attributes(self):
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
            attribute = ShaderUniform(namebuf.value.decode("utf-8"), uniform_size.value, uniform_type.value, location)
            self._attributes[attribute.name] = attribute

    def dump_variables(self):
        for u in list(self._uniforms.values()) + list(self._attributes.values()):
            print("%3s %6s %2s %s" % (u.location, u.type, u.size, u.name))