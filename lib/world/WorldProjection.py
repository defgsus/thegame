import glm


class WorldProjection:

    P_ORTHO = "o"
    P_ISOMETRIC = "i"
    P_PERSPECTIVE = "p"
    P_EGO = "e"

    PROJECTIONS = (
        P_ORTHO,
        P_ISOMETRIC,
        P_PERSPECTIVE,
        P_EGO,
    )

    def __init__(self, width, height, projection=P_ORTHO):
        self.projection = projection
        self.width = width
        self.height = height

        self._zoom = 0.
        self._rotation = glm.vec3(0)
        self._matrix = glm.mat4(1)

        self._szoom = 0.
        self._srotation = glm.vec3(0)
        self._smatrix = glm.mat4(1)

        self.init()

    @property
    def zoom(self):
        return self._szoom

    @zoom.setter
    def zoom(self, val):
        self._zoom = val

    @property
    def rotation(self):
        return self._srotation

    @rotation.setter
    def rotation(self, val):
        self._rotation = val

    @property
    def matrix(self):
        return self._smatrix

    @matrix.setter
    def matrix(self, val):
        self._matrix = val

    @property
    def near(self):
        return self._near

    @property
    def far(self):
        return self._far

    def init(self, projection=None):
        if projection is not None:
            self.projection = projection

        if self.projection in "oi":
            self._near = -100
            self._far = 100
        else:
            self._near = 0.01
            self._far = 100

        self._init_rotation()
        self._calc_matrix()

    def update(self, dt):
        d = min(1, dt * 5)
        self._szoom += d + (self._zoom - self._szoom)
        self._srotation += d * (self._rotation - self._srotation)

        self._calc_matrix()

        d = min(1, dt * 3)
        self._smatrix += d * (self._matrix - self._smatrix)

    def get_ray(self, uv):
        ro = self.matrix * glm.vec4(uv, self.near, 1)
        rd = glm.normalize(
            self.matrix * glm.vec4(uv, self.far, 1) - ro
        )
        return glm.vec3(ro), glm.vec3(rd)

    def _init_rotation(self):
        self._rotation = glm.vec3(
            -glm.pi()/(3.3 if self.projection=="i" else 4),
            0, 0)
        if self.projection == "e":
            self._rotation[0] = -glm.pi()/2.
        if self.projection == "i":
            self._rotation[2] = glm.pi()/4.

    def _calc_matrix(self):
        sc = 16
        asp = self.width / self.height

        if self.projection == "i":
            ysc = sc/asp
            proj = glm.ortho(-sc,sc, -ysc,ysc, self._near, self._far)
        elif self.projection == "o":
            ysc = sc/asp * .75
            proj = glm.ortho(-sc,sc, -ysc,ysc, self._near, self._far)
        elif self.projection == "p":
            proj = glm.perspectiveFov(1., self.width, self.height, self._near, self._far)
            proj = glm.translate(proj, (0,0,-5))
        else:  # "e"
            proj = glm.perspectiveFov(2., self.width, self.height, self._near, self._far)
            proj = glm.translate(proj, (0,0,0))

        proj = glm.rotate(proj, self._srotation[0], (1,0,0))
        proj = glm.rotate(proj, self._srotation[1], (0,1,0))
        proj = glm.rotate(proj, self._srotation[2], (0,0,1))
        proj = glm.translate(proj, (0, 0,
                                    [-3,-2,-4,-1]["oipe".index(self.projection)]))

        proj = glm.scale(proj, glm.vec3(max(0.01, 1.+self.zoom/10.)))
        self._matrix = proj


