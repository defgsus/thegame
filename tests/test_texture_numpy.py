import unittest
from typing import Optional

import numpy as np
from pyglet import gl

from lib.opengl.core import Texture2D


class TestTextureNumpy(unittest.TestCase):

    def check_texture(
            self,
            array: np.ndarray,
            width: Optional[int] = None,
            input_format: Optional[int] = None,
            input_type: Optional[int] = None,
            output_format: Optional[int] = None,
            gpu_format: int = gl.GL_RGBA,
            expect_width: Optional[int] = None,
            expect_height: Optional[int] = None,
    ):
        tex = Texture2D()
        tex.create()
        tex.bind()
        tex.upload_numpy(
            array=array, width=width,
            input_format=input_format, input_type=input_type, gpu_format=gpu_format
        )

        if expect_width is None and width is not None:
            expect_width = width
        if expect_width is not None:
            self.assertEqual(expect_width, tex.width, f"for {array.shape}")
        if expect_height is not None:
            self.assertEqual(expect_height, tex.height, f"for {array.shape}")

        if output_format is None:
            output_format = input_format if input_format is not None else gl.GL_LUMINANCE

        #test_array = np.ones([6, 3], dtype="int32")
        #ptr = np.ctypeslib.as_ctypes(test_array)
        #gl.glGetTexImage(tex.target, 0, gl.GL_RED, gl.GL_INT, ptr)

        ret_array = tex.to_numpy(format=output_format)
        flat_in = array.flatten()
        flat_out = ret_array.flatten()
        self.assertEqual(flat_in.shape, flat_out.shape)

        if np.any(np.abs(flat_in - flat_out) > 1./256.):
            raise AssertionError(
                f"Returned array differs!\n\noriginal:\n{array}\n\nreturned:\n{ret_array}"
            )

        #print(array.shape, ret_array.shape)
        #print(flat_in)
        #print(flat_out)
        #print(ret_array)

    def test_red_float(self):
        self.check_texture(
            np.array([.5, 1., 1.5, 2., 2.5, 3.], dtype="float32"),
            width=3,
            input_format=gl.GL_RED,
            gpu_format=gl.GL_R32F,
        )

    # does not work in opengl 2.1
    @unittest.expectedFailure
    def test_red_int(self):
        self.check_texture(
            np.array([1, 2, 3, 4, 5, 6], dtype="int32"),
            width=2,
            input_format=gl.GL_RED,
            input_type=gl.GL_INT,
            gpu_format=gl.GL_R32I,
        )

    def test_float_raw(self):
        width, height = 8, 4
        gpu_format = gl.GL_R32F
        input_format = gl.GL_RED
        input_type = gl.GL_FLOAT
        in_array = np.linspace(0, width*height-1, num=width*height, dtype="float32")
        ptr = np.ctypeslib.as_ctypes(in_array)

        tex = Texture2D()
        tex.create()
        tex.bind()
        gl.glTexImage2D(
            tex.target, 0, gpu_format, width, height, 0,
            input_format, input_type, ptr
        )

        out_array = np.zeros([height * width], dtype="float32")
        ptr = np.ctypeslib.as_ctypes(out_array)

        gl.glGetTexImage(tex.target, 0, gl.GL_RED, gl.GL_FLOAT, ptr)

        print(in_array)
        print(out_array)
