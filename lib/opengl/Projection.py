import glm


class Projection:

    """
    Wrapper around an initialized projection matrix

    The `transformation_matrix` property can be replaced with a custom transformation matrix
    """

    P_ORTHO = "o"
    P_PERSPECTIVE = "p"

    PROJECTIONS = (
        P_ORTHO,
        P_PERSPECTIVE,
    )

    def __init__(self, width, height, projection=P_PERSPECTIVE):
        self.projection = projection
        self.width = width
        self.height = height

        self.user_transformation = None

        self._mat_project = glm.mat4(1)
        self._mat_transform = glm.mat4(1)

        self.init()

    def __str__(self):
        return "Projection('%s', %sx%s)" % (self.projection, self.width, self.height)

    @property
    def matrix(self):
        return self._mat_project * self._mat_transform

    @property
    def projection_matrix(self):
        return self._mat_project

    @property
    def inverse_projection_matrix(self):
        return glm.inverse(self._mat_project)

    @property
    def transformation_matrix(self):
        return self._mat_transform

    @transformation_matrix.setter
    def transformation_matrix(self, trans):
        self._mat_transform = trans

    @property
    def near(self):
        return self._near

    @property
    def far(self):
        return self._far

    def is_perspective(self):
        return self.projection == self.P_PERSPECTIVE

    def get_direction(self, dir):
        """Transforms vec3 direction to a direction matching the current transformation"""
        dir = glm.inverse(self.transformation_matrix) * glm.vec4(dir, 0)
        return glm.vec3(dir)

    def init(self, projection=None):
        if projection is not None:
            self.projection = projection

        if self.projection == self.P_ORTHO:
            self._near = -30
            self._far = 100
        else:
            self._near = 0.01
            self._far = 100

        self._calc_projection_matrix()

    def update(self, dt):
        pass

    def screen_to_ray(self, x, y, scr_width, scr_height):
        """Return tuple with ray-origin and normalized ray-direction for input screen coords"""
        x = x / scr_width * 2. - 1.
        y = y / scr_height * 2. - 1.
        if scr_height < scr_width:
            x /= scr_height / scr_width
        else:
            y /= scr_width / scr_height

        if self.height < self.width:
            x /= self.width / self.height
        else:
            y /= self.height / self.width
        return self.voxel_to_ray(
            (x * .5 + .5) * self.width,
            (y * .5 + .5) * self.height,
        )

    def voxel_to_ray(self, x, y):
        """Return tuple with ray-origin and normalized ray-direction for input render-res x, y"""
        st = glm.vec2(x / self.width, y / self.height) * 2. - 1.

        if self.is_perspective():
            near, far = -self.near, -self.far
        else:
            near, far = -1, 1
        pos = self.inverse_projection_matrix * glm.vec4(st.x, st.y, near, 1)
        pos /= pos.w

        dirf = self.inverse_projection_matrix * glm.vec4(st.x, st.y, far, 1)
        dirf /= dirf.w
        dir = glm.normalize(glm.vec3(dirf-pos))

        t = glm.inverse(self.transformation_matrix)
        ro, rd = glm.vec3(t * pos), glm.normalize(glm.vec3(t * glm.vec4(dir, 0)))
        if self.is_perspective():
            rd = -rd
        if 0:
            def _v(v):
                return "(%s)" % ", ".join("%s"%round(x,2) for x in v)
            print("near", _v(pos), "far", _v(dirf), "ro", _v(ro), "rd", _v(rd))
        return ro, rd

    def _calc_projection_matrix(self):
        sc = 11
        asp = self.width / self.height

        # projection

        if self.projection == self.P_ORTHO:
            ysc = sc/asp * .75
            proj = glm.ortho(-sc,sc, -ysc,ysc, self._near, self._far)
        elif self.projection == self.P_PERSPECTIVE:
            proj = glm.perspectiveFov(1., self.width, self.height, self._near, self._far)
        else:
            raise ValueError(f"unknown projection type '{self.projection}'")

        self._mat_project = proj
