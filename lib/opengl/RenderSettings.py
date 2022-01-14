from typing import Optional

#from lib.world.WorldProjection import WorldProjection
from .Projection import Projection


class RenderSettings:
    
    def __init__(
            self,
            render_width: int,
            render_height: int,
            projection: Optional[Projection] = None,
            mag_filter: Optional[int] = None,
    ):
        self.render_width = render_width
        self.render_height = render_height
        self.screen_width = render_width
        self.screen_height = render_height
        self.projection = projection or Projection(self.render_width, self.render_height)
        self.mag_filter = mag_filter
        self.time = 0.

    def __str__(self):
        return "%s(screen=%sx%s, render=%sx%s, proj=%s)" % (
            self.__class__.__name__,
            self.screen_width, self.screen_height,
            self.render_width, self.render_height,
            self.projection,
        )

    def __repr__(self):
        return self.__str__()

    def set_size(self, width: int, height: int):
        self.render_width = width
        self.render_height = height
        self.screen_width = width
        self.screen_height = height

    def screen_to_ray(self, x: float, y: float):
        return self.projection.screen_to_ray(x, y, self.screen_width, self.screen_height)
