from typing import Optional

import numpy as np

from .TextureBase import *
from .types import (
    OPENGL_ENUM_CHANNELSIZE_MAPPING,
    CHANNELSIZE_OPENGL_ENUM_MAPPING,
    NUMPY_DTYPE_TO_OPENGL_TYPE_ENUM_MAPPING,
    gl_enum_to_string,
)


class Texture2D(TextureBase):

    def __init__(self, multi_sample: int = 0, name: Optional[str] = None):
        target = GL_TEXTURE_2D if multi_sample < 1 else GL_TEXTURE_2D_MULTISAMPLE
        super(Texture2D, self).__init__(target, name=name)
        self.multi_sample = multi_sample

    def __str__(self):
        return "Texture2D(%s, %sx%s, h=%s)" % (
            self.name, self.width, self.height, self.handle,
        )

    def size(self):
        return self.width, self.height

    def upload(
            self,
            values,
            width: int,
            height: int,
            input_format: int = GL_RGB,
            input_type: int = GL_FLOAT,
            gpu_format: int = GL_RGBA,
            mipmap_level: int = 0,
            do_flip_y: bool = False,
    ):
        """Upload linear data in `values`. height == len(values) / width / typesize(input_format).
        `values` can be None to create an empty texture"""
        self.width = width
        self.height = height
        self.gpu_format = gpu_format

        if do_flip_y:
            values = self._flip_y(values, width, height, get_opengl_channel_size(input_format))

        if values is not None:
            if isinstance(values, (list, tuple)):
                ptr = (get_opengl_type(input_type) * len(values))(*values)
            elif isinstance(values, np.ndarray):
                ptr = np.ctypeslib.as_ctypes(values)
            else:
                raise TypeError(f"Texture of type '{type(values).__name__}' not supported")
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

        values = image.get_image_data().get_data()
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

    def upload_numpy(
            self,
            array: np.ndarray,
            width: Optional[int] = None,
            input_format: Optional[int] = None,
            input_type: Optional[int] = None,
            gpu_format: int = GL_RGBA,
            mipmap_level: int = 0,
    ):
        ndim, shape, dtype = array.ndim, array.shape, str(array.dtype)

        if ndim == 1:
            if width is None:
                raise ValueError(f"Need to provide 'width' for one-dimensional numpy array, shape {shape}")

            if input_format is None:
                num_colors = shape[0] / width
                if num_colors != int(num_colors):
                    raise ValueError(
                        f"Need to specify 'input_format' for numpy array with shape {shape}"
                        f", width {width} and shape do not align"
                    )
                num_colors = int(num_colors)
                input_format = CHANNELSIZE_OPENGL_ENUM_MAPPING.get(int(num_colors))
                if input_format is None:
                    raise ValueError(
                        f"Need to specify 'input_format' for numpy array with shape {shape}"
                        f", width {width} would suggest {num_colors} colors"
                    )
            else:
                num_colors = OPENGL_ENUM_CHANNELSIZE_MAPPING[input_format]

            height = shape[0] // width // num_colors

        elif ndim == 2:
            if width is None:
                if input_format is None:
                    height, width = shape
                    input_format = GL_LUMINANCE
                else:
                    num_colors = OPENGL_ENUM_CHANNELSIZE_MAPPING[input_format]
                    width = shape[0] / num_colors
                    if width != int(width):
                        raise ValueError(
                            f"Need to specify 'width' for numpy array with shape {shape} "
                            f"and input_format {input_format}"
                        )
                    width = int(width)
                    height = shape[0]
            else:
                height = shape[0]
                if input_format is None:
                    num_colors = shape[0] / width
                    if num_colors != int(num_colors):
                        raise ValueError(
                            f"Need to specify 'input_format' for numpy array with shape {shape}"
                            f", width {width} and shape do not align"
                        )
                    input_format = CHANNELSIZE_OPENGL_ENUM_MAPPING.get(int(num_colors))
                    if input_format is None:
                        raise ValueError(
                            f"Need to specify 'input_format' for numpy array with shape {shape}"
                            f", width {width} would suggest {num_colors} colors"
                        )

        else:
            raise ValueError(f"Can not convert numpy array of shape {shape} to texture")

        if input_type is None:
            input_type = NUMPY_DTYPE_TO_OPENGL_TYPE_ENUM_MAPPING[dtype]
            if input_type is None:
                raise ValueError(f"Need to specify 'input_type' for numpy array with dtype {dtype}")

        print("UPLOAD", width, height, gl_enum_to_string(input_format),
              gl_enum_to_string(input_type), gl_enum_to_string(gpu_format))

        self.upload(
            array, width, height, input_format, input_type,
            gpu_format=gpu_format,
            mipmap_level=mipmap_level,
        )

    def to_numpy(
            self,
            format: int = GL_RGB,
            dtype: str = "float32",
            mipmap_level: int = 0,
    ) -> np.ndarray:
        """
        format: GL_STENCIL_INDEX, GL_DEPTH_COMPONENT, GL_DEPTH_STENCIL, GL_RED, GL_GREEN, GL_BLUE, GL_RG, GL_RGB,
                GL_RGBA, GL_BGR, GL_BGRA, GL_RED_INTEGER, GL_GREEN_INTEGER, GL_BLUE_INTEGER, GL_RG_INTEGER,
                GL_RGB_INTEGER, GL_RGBA_INTEGER, GL_BGR_INTEGER, GL_BGRA_INTEGER
        type: GL_UNSIGNED_BYTE, GL_BYTE, GL_UNSIGNED_SHORT, GL_SHORT, GL_UNSIGNED_INT, GL_INT, GL_HALF_FLOAT, GL_FLOAT,
              GL_UNSIGNED_BYTE_3_3_2, GL_UNSIGNED_BYTE_2_3_3_REV, GL_UNSIGNED_SHORT_5_6_5, GL_UNSIGNED_SHORT_5_6_5_REV,
              GL_UNSIGNED_SHORT_4_4_4_4, GL_UNSIGNED_SHORT_4_4_4_4_REV, GL_UNSIGNED_SHORT_5_5_5_1,
              GL_UNSIGNED_SHORT_1_5_5_5_REV, GL_UNSIGNED_INT_8_8_8_8, GL_UNSIGNED_INT_8_8_8_8_REV,
              GL_UNSIGNED_INT_10_10_10_2, GL_UNSIGNED_INT_2_10_10_10_REV, GL_UNSIGNED_INT_24_8,
              GL_UNSIGNED_INT_10F_11F_11F_REV, GL_UNSIGNED_INT_5_9_9_9_REV, and GL_FLOAT_32_UNSIGNED_INT_24_8_REV
        """
        type = NUMPY_DTYPE_TO_OPENGL_TYPE_ENUM_MAPPING[dtype]

        num_colors = OPENGL_ENUM_CHANNELSIZE_MAPPING[format]
        array = np.ndarray([self.height, self.width, num_colors], dtype=dtype)
        ptr = np.ctypeslib.as_ctypes(array)

        glGetTexImage(self.target, mipmap_level, format, type, ptr)
        return array

    def _flip_y(self, values, width, height, num_chan):
        ret = []
        for i in range(height, 0, -1):
            ret += values[(i-1)*width*num_chan:i*width*num_chan]
        return ret