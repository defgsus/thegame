import ctypes
from .base import *
pyglet.options['debug_texture'] = True

class Texture2D(OpenGlBaseObject):

    def __init__(self, name=None):
        super(Texture2D, self).__init__(name=name)
        self.target = GL_TEXTURE_2D
        self.width = 0
        self.height = 0
        self.gpu_format = 0

    def _create(self):
        h = GLuint(0)
        glGenTextures(1, ctypes.byref(h))
        self._handle = h.value

    def _release(self):
        glDeleteTextures(0, self._handle)

    def _bind(self):
        glBindTexture(self.target, self._handle)

    def _unbind(self):
        glBindTexture(self.target, 0)

    def set_parameter(self, enum, value):
        glTexParameteri(self.target, enum, value)

    def upload(self, values, width, height, input_format=GL_RGB, input_type=GL_FLOAT, gpu_format=GL_RGBA, mipmap_level=0):
        """Upload linear data in `values`. height == len(values) / width / typesize(input_format).
        `values` can be None to create an empty texture"""
        self.width = width
        self.height = height
        self.gpu_format = gpu_format

        if values is not None:
            ptr = (get_opengl_type(input_type) * len(values))(*values)
        else:
            ptr = None

        glTexImage2D(self.target, mipmap_level, self.gpu_format, self.width, self.height, 0,
                     input_format, input_type, ptr)

        self.set_parameter(GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        self.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.set_parameter(GL_TEXTURE_WRAP_S, GL_REPEAT)
        self.set_parameter(GL_TEXTURE_WRAP_T, GL_REPEAT)

    def upload_image(self, image_or_file, mipmap_level=0, gpu_format=GL_RGBA):
        image = pyglet.image.load(image_or_file)
        if image.format == "RGB":
            input_format = GL_RGB
        elif image.format == "RGBA":
            input_format = GL_RGBA
        else:
            raise ValueError("Unsupported image format %s" % image.format)

        values = image.data
        #values = [v for v in values]
        #print(values)
        self.upload(values, image.width, image.height, input_format=input_format, input_type=GL_UNSIGNED_BYTE,
                    mipmap_level=mipmap_level, gpu_format=gpu_format)

    def upload_image_PIL(self, image_or_file, mipmap_level=0, gpu_format=GL_RGBA):
        from PIL import Image
        if isinstance(image_or_file, Image.Image):
            image = image_or_file
        else:
            image = Image.open(image_or_file)

        try:
            num_chan = len(image.getpixel((0, 0)))
        except TypeError:
            num_chan = 1
        print(image.getpixel((0, 0)))
        input_format = [GL_LUMINANCE, GL_RG, GL_RGB, GL_RGBA][num_chan-1]

        values = image.tobytes("raw")
        values = [v for v in values]
        print(values)
        self.upload(values, image.width, image.height, input_format=input_format, input_type=GL_UNSIGNED_BYTE,
                    mipmap_level=mipmap_level, gpu_format=gpu_format)
