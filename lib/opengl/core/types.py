import ctypes
from pyglet.gl import *
from pyglet import gl


OPENGL_TYPE_ENUM_MAPPING = {
    GLbyte: GL_BYTE,
    GLubyte: GL_UNSIGNED_BYTE,
    GLchar: GL_BYTE,

    GLshort: GL_SHORT,
    GLushort: GL_UNSIGNED_SHORT,

    GLint: GL_INT,
    GLuint: GL_UNSIGNED_INT,

    GLfloat: GL_FLOAT,
    GLdouble: GL_DOUBLE,
}

OPENGL_ENUM_TYPE_MAPPING = {OPENGL_TYPE_ENUM_MAPPING[t]: t for t in OPENGL_TYPE_ENUM_MAPPING}


# TODO: need to add BGR and variants
OPENGL_ENUM_CHANNELSIZE_MAPPING = {
    GL_RED: 1,
    GL_GREEN: 1,
    GL_BLUE: 1,
    GL_LUMINANCE: 1,
    GL_ALPHA: 1,

    GL_LUMINANCE_ALPHA: 2,

    GL_RGB: 3,
    GL_R3_G3_B2: 3,
    GL_RGB4: 3,
    GL_RGB5: 3,
    GL_RGB8: 3,
    GL_RGB10: 3,
    GL_RGB12: 3,
    GL_RGB16: 3,
    GL_BGR: 3,

    GL_RGBA: 4,
    GL_RGBA2: 4,
    GL_RGBA4: 4,
    GL_RGB5_A1: 4,
    GL_RGBA8: 4,
    GL_RGB10_A2: 4,
    GL_RGBA12: 4,
    GL_RGBA16: 4,
    GL_RGBA32F:	4,
}

CHANNELSIZE_OPENGL_ENUM_MAPPING = {
    1: GL_LUMINANCE,
    2: GL_RG,
    3: GL_RGB,
    4: GL_RGBA,
}

NUMPY_DTYPE_TO_OPENGL_TYPE_ENUM_MAPPING = {
    "uint8": GL_UNSIGNED_BYTE,
    "int8": GL_BYTE,
    "uint16": GL_UNSIGNED_SHORT,
    "int16": GL_SHORT,
    "uint32": GL_UNSIGNED_INT,
    "int32": GL_INT,
    "float32": GL_FLOAT,
    "float64": GL_DOUBLE,
}


def get_opengl_type_enum(typ):
    if typ in OPENGL_TYPE_ENUM_MAPPING:
        return OPENGL_TYPE_ENUM_MAPPING[typ]
    return typ


def get_opengl_type(enum):
    if enum in OPENGL_ENUM_TYPE_MAPPING:
        return OPENGL_ENUM_TYPE_MAPPING[enum]
    return enum


def get_opengl_type_size(enum_or_type):
    typ = get_opengl_type(enum_or_type)
    return ctypes.sizeof(typ)


def get_opengl_channel_size(enum):
    return OPENGL_ENUM_CHANNELSIZE_MAPPING.get(enum, 0)


def gl_enum_to_string(enum: int) -> str:
    for name in dir(gl):
        if getattr(gl, name) == enum:
            return name
    return str(enum)

