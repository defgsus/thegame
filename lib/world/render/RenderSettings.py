from lib.world.WorldProjection import WorldProjection


class RenderSettings:
    
    def __init__(self, render_width, render_height):
        self.render_width = render_width
        self.render_height = render_height
        self.screen_width = render_width
        self.screen_height = render_height
        self.projection = WorldProjection(self.render_width, self.render_height, WorldProjection.P_ISOMETRIC)
        self.projection.update(.4)
        self.time = 0.
