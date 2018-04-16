from .TextureBase import *


class Texture3D(TextureBase):

    def __init__(self, name=None):
        super(Texture3D, self).__init__(GL_TEXTURE_3D, name=name)
        self.depth = 0

    def size(self):
        return self.width, self.height, self.depth

    def infostr(self):
        return "%sx%sx%s" % (self.width, self.height, self.depth)

    def upload(self, values, width, height, depth,
               input_format=GL_RGB, input_type=GL_FLOAT, gpu_format=GL_RGBA, mipmap_level=0):
        """Upload linear data in `values`.
        `values` can be None to create an empty texture"""
        self.width = width
        self.height = height
        self.depth = depth
        self.gpu_format = gpu_format

        if values is not None:
            ptr = (get_opengl_type(input_type) * len(values))(*values)
        else:
            ptr = None

        glTexImage3D(self.target, mipmap_level, self.gpu_format, self.width, self.height, self.depth, 0,
                     input_format, input_type, ptr)

        self.set_parameter(GL_TEXTURE_MIN_FILTER, self.min_filter)
        self.set_parameter(GL_TEXTURE_MAG_FILTER, self.mag_filter)

        self.set_parameter(GL_TEXTURE_WRAP_R, self.wrap_mode)
        self.set_parameter(GL_TEXTURE_WRAP_S, self.wrap_mode)
        self.set_parameter(GL_TEXTURE_WRAP_T, self.wrap_mode)


