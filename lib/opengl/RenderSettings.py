from typing import Optional

#from lib.world.WorldProjection import WorldProjection
from .Projection import Projection


class RenderSettings:
    
    def __init__(
            self,
            render_width: int,
            render_height: int,
            projection: Optional[Projection] = None,
    ):
        self.render_width = render_width
        self.render_height = render_height
        self.screen_width = render_width
        self.screen_height = render_height
        self.projection = projection or Projection(self.render_width, self.render_height)
        self.time = 0.

    def __str__(self):
        return "RenderSettings(screen=%sx%s, render=%sx%s, proj=%s)" % (
            self.screen_width, self.screen_height,
            self.render_width, self.render_height,
            self.projection,
        )

    def __repr__(self):
        return self.__str__()

    def screen_to_ray(self, x: float, y: float):
        return self.projection.screen_to_ray(x, y, self.screen_width, self.screen_height)
