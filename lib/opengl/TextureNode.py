from pathlib import Path
from typing import Union, Optional, Callable

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
            texture: Optional[Texture2D] = None,
            callback: Optional[Callable[[RenderSettings, Texture2D], None]] = None,
            name: Optional[str] = None,
    ):
        assert filename or texture or callback, "Must define filename, texture or callback"
        self.filename = None if filename is None else Path(filename)
        name = name or (self.filename.name if self.filename else "tex2d")
        super().__init__(name)
        self.texture: Optional[Texture2D] = texture or None
        self.callback = callback

    def create(self, render_settings: RenderSettings):
        if not self.texture:
            self.texture = Texture2D()

        if not self.texture.is_created():
            self.texture.create()

        self.texture.set_active_texture(0)
        self.texture.bind()

        if self.filename is not None:
            self.texture.upload_image(str(self.filename))

        elif self.callback is not None:
            self.callback(render_settings, self.texture)

    def release(self):
        self.texture.release()

    def render(self, render_settings: RenderSettings, pass_num: int):
        self.texture.set_active_texture(0)
        self.texture.bind()
