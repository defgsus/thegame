from pathlib import Path
from typing import Union, Optional

from pyglet import gl
import numpy as np

from .RenderNode import RenderNode
from .RenderSettings import RenderSettings
from .core import Texture2D
from .core.types import CHANNELSIZE_OPENGL_ENUM_MAPPING


class Texture2DNode(RenderNode):

    def __init__(
            self,
            filename: Optional[Union[str, Path]] = None,
            data: Optional[np.ndarray] = None,
            texture: Optional[Texture2D] = None,
            name: Optional[str] = None,
    ):
        assert filename or texture or data is not None, "Must define filename or texture or data"
        self.filename = None if filename is None else Path(filename)
        name = name or (self.filename.name if self.filename else "tex2d")
        super().__init__(name)
        self.texture: Optional[Texture2D] = texture or None
        self.data = data

    def create(self, render_settings: RenderSettings):
        if not self.texture:
            self.texture = Texture2D()

        if not self.texture.is_created():
            self.texture.create()

        self.texture.set_active_texture(0)
        self.texture.bind()

        if self.filename:
            self.texture.upload_image(str(self.filename))

        elif self.data is not None:
            if self.data.ndim == 2:
                format = gl.GL_RED
            elif self.data.ndim == 3:
                if self.data.shape[0] not in CHANNELSIZE_OPENGL_ENUM_MAPPING:
                    raise ValueError(f"Can not convert data of shape {self.data.shape} to texture")
                format = CHANNELSIZE_OPENGL_ENUM_MAPPING[self.data.shape[0]]
            else:
                raise ValueError(f"Can not convert data of shape {self.data.shape} to texture")

            self.texture.upload(self.data, self.data.shape[-1], self.data.shape[-2], format)

    def release(self):
        self.texture.release()

    def render(self, render_settings: RenderSettings, pass_num: int):
        self.texture.set_active_texture(0)
        self.texture.bind()
