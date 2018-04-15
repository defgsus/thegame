from .TextureBase import *


class Texture2D(TextureBase):

    def __init__(self, multi_sample=0, name=None):
        target = GL_TEXTURE_2D if multi_sample < 1 else GL_TEXTURE_2D_MULTISAMPLE
        super(Texture2D, self).__init__(target, name=name)
        self.multi_sample = multi_sample

    def __str__(self):
        return "Texture2D(%s, %sx%s)" % (self.name, self.width, self.height)

    def upload(self, values, width, height, input_format=GL_RGB, input_type=GL_FLOAT, gpu_format=GL_RGBA, mipmap_level=0,
               do_flip_y=False):
        """Upload linear data in `values`. height == len(values) / width / typesize(input_format).
        `values` can be None to create an empty texture"""
        self.width = width
        self.height = height
        self.gpu_format = gpu_format

        if do_flip_y:
            values = self._flip_y(values, width, height, get_opengl_channel_size(input_format))

        if values is not None:
            ptr = (get_opengl_type(input_type) * len(values))(*values)
        else:
            ptr = None

        if self.multi_sample < 1:
            glTexImage2D(self.target, mipmap_level, self.gpu_format, self.width, self.height, 0,
                         input_format, input_type, ptr)
        else:
            glTexImage2DMultisample(self.target, self.multi_sample, self.gpu_format, self.width, self.height, GL_TRUE)

        self.set_parameter(GL_TEXTURE_MIN_FILTER, self.min_filter)
        self.set_parameter(GL_TEXTURE_MAG_FILTER, self.mag_filter)

        self.set_parameter(GL_TEXTURE_WRAP_S, self.wrap_mode)
        self.set_parameter(GL_TEXTURE_WRAP_T, self.wrap_mode)

    def upload_image(self, filename, mipmap_level=0, gpu_format=GL_RGBA, do_flip_y = False):
        image = pyglet.image.load(filename)
        if image.format == "RGB":
            num_chan = 3
            input_format = GL_RGB
        elif image.format == "RGBA":
            num_chan = 4
            input_format = GL_RGBA
        else:
            raise ValueError("Unsupported image format %s" % image.format)

        values = image.data
        if not do_flip_y:
            values = self._flip_y(values, image.width, image.height, num_chan)
        self.upload(values, image.width, image.height, input_format=input_format, input_type=GL_UNSIGNED_BYTE,
                    mipmap_level=mipmap_level, gpu_format=gpu_format)

    def upload_image_PIL(self, image_or_file, mipmap_level=0, gpu_format=GL_RGBA, do_flip_y=False):
        from PIL import Image
        if isinstance(image_or_file, Image.Image):
            image = image_or_file
        else:
            image = Image.open(image_or_file)

        try:
            num_chan = len(image.getpixel((0, 0)))
        except TypeError:
            num_chan = 1
        input_format = [GL_LUMINANCE, GL_RG, GL_RGB, GL_RGBA][num_chan-1]

        values = image.tobytes("raw")
        if not do_flip_y:
            values = self._flip_y(values, image.width, image.height, num_chan)
        self.upload(values, image.width, image.height, input_format=input_format, input_type=GL_UNSIGNED_BYTE,
                    mipmap_level=mipmap_level, gpu_format=gpu_format)

    def _flip_y(self, values, width, height, num_chan):
        ret = []
        for i in range(height, 0, -1):
            ret += values[(i-1)*width*num_chan:i*width*num_chan]
        return ret