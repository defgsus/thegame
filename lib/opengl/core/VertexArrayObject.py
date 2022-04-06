from typing import Optional

from .base import *
from tests.util import Timer


class BufferObject(OpenGlBaseObject):

    def __init__(self, target: GLenum, storage_type: GLenum = GL_STATIC_DRAW, name: Optional[str] = None):
        """
        target is one of GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, etc..
        """
        super(BufferObject, self).__init__(name=name)
        self.target = target
        self.size = None
        self.storage_type = storage_type
        self.divisor = 0
        self.offset = 0

    def _create(self):
        handles = (GLuint * 1)(0)
        glGenBuffers(1, handles)
        self._handle = handles[0]

    def _release(self):
        handles = (GLuint * 1)(self._handle)
        glDeleteBuffers(1, handles)
        self._handle = None

    def _bind(self):
        glBindBuffer(self.target, self._handle)

    def _unbind(self):
        glBindBuffer(self.target, 0)

    def upload(self, Type, values):
        """
        Uploads the buffer data.
        Buffer must be bound.
        """
        self.check_created("upload")
        ptr = (Type * len(values))(*values)
        self.size = ctypes.sizeof(Type) * len(values)
        #print("upload", self.target, self.size, ptr, self.storage_type)
        glBufferData(self.target, self.size, ptr, self.storage_type)


class ArrayBufferObject(BufferObject):

    def __init__(self, storage_type: GLenum = GL_STATIC_DRAW, name: Optional[str] = None):
        super().__init__(GL_ARRAY_BUFFER, storage_type, name)
        self.attribute_location = 0
        self.stride = 0
        self.normalized = False
        self.type_enum = None
        self.num_dimensions = 1
        self.divisor = 0

    def set_attrib_pointer(self):
        glEnableVertexAttribArray(self.attribute_location)
        glVertexAttribPointer(
            self.attribute_location, self.num_dimensions, self.type_enum, self.normalized, self.stride, self.offset,
        )
        glVertexAttribDivisor(self.attribute_location, self.divisor or 0)


class ElementArrayBufferObject(BufferObject):

    def __init__(self, storage_type: GLenum = GL_STATIC_DRAW, name: Optional[str] = None):
        super().__init__(GL_ELEMENT_ARRAY_BUFFER, storage_type, name)


class VertexArrayObject(OpenGlBaseObject):

    def _create(self):
        handles = (GLuint * 1)(0)
        glGenVertexArrays(1, handles)
        self._handle = handles[0]
        self._attrib_buffers = []
        self._element_buffers = []

    def _release(self):
        handles = (GLuint * 1)(self._handle)
        glDeleteVertexArrays(1, handles)
        self._handle = None

    def _bind(self):
        glBindVertexArray(self._handle)

    def _unbind(self):
        glBindVertexArray(0)

    def clear(self):
        """Release and clear all attribute and element buffers"""
        for buf in self._attrib_buffers:
            if buf.is_created():
                buf.release()
        self._attrib_buffers.clear()
        for buf in self._element_buffers:
            if buf.is_created():
                buf.release()
        self._element_buffers.clear()

    def create_attribute_buffer(
            self,
            attribute_location: int,
            num_dimensions: int,
            Type,
            values,
            stride: int = 0,
            offset: Optional[int] = None,
            storage_type: GLenum = GL_STATIC_DRAW,
            normalized: bool = False,
            divisor: int = 0,
    ) -> ArrayBufferObject:
        """
        Creates a vertex attribute array buffer.

        The vertex array object needs to be bound.

        Use `divisor` for "instanced drawing" (https://learnopengl.com/Advanced-OpenGL/Instancing)
        """
        self.check_created("create_attribute_buffer")
        buf = ArrayBufferObject(storage_type, name=f"{self.name}-attr-{len(self._attrib_buffers)}")
        buf.attribute_location = attribute_location
        buf.type_enum = get_opengl_type_enum(Type)
        buf.num_dimensions = num_dimensions
        buf.normalized = normalized
        buf.stride = stride
        buf.offset = offset
        buf.divisor = divisor

        buf.create()
        buf.bind()
        buf.upload(Type, values)
        buf.set_attrib_pointer()

        self._attrib_buffers.append(buf)
        return buf

    def create_element_buffer(
            self,
            primitive_type, Type, values,
            storage_type=GL_STATIC_DRAW):
        self.check_created("create_index_buffer")
        buf = ElementArrayBufferObject(storage_type, name=f"{self.name}-index-{len(self._element_buffers)}")
        buf.primitive_type = primitive_type
        buf.num_vertices = len(values)
        buf.type_enum = get_opengl_type_enum(Type)

        buf.create()
        buf.bind()
        buf.upload(Type, values)

        self._element_buffers.append(buf)
        return buf

    def draw_elements(self, num_instances: Optional[int] = None):
        """Draws all element_buffers"""
        with Timer() as timer:
            for abuf in self._attrib_buffers:
                abuf.bind()
                abuf.set_attrib_pointer()
        # print(timer.fps())

        for elembuf in self._element_buffers:
            elembuf.bind()

            #print("DRAW", elembuf.primitive_type, elembuf.num_vertices, elembuf.type_enum)
            if num_instances is None:
                glDrawElements(elembuf.primitive_type, elembuf.num_vertices, elembuf.type_enum, None)
            else:
                glDrawElementsInstanced(
                    elembuf.primitive_type, elembuf.num_vertices, elembuf.type_enum, None,
                    num_instances,
                )
