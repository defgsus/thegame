from lib.world.WorldProjection import WorldProjection


class RenderSettings:
    
    def __init__(self, render_width, render_height, projection=WorldProjection.P_PERSPECTIVE):
        self.render_width = render_width
        self.render_height = render_height
        self.screen_width = render_width
        self.screen_height = render_height
        self.projection = WorldProjection(self.render_width, self.render_height, projection)
        self.projection.update(.4)
        self.time = 0.

    def __str__(self):
        return "RenderSettings(screen=%sx%s, render=%sx%s, proj=%s)" % (
            self.screen_width, self.screen_height,
            self.render_width, self.render_height,
            self.projection,
        )

    def __repr__(self):
        return self.__str__()

    def screen_to_ray(self, x, y):
        return self.projection.screen_to_ray(x, y, self.screen_width, self.screen_height)