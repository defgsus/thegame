import glm


class WorldProjection:

    P_TOP = "t"
    P_ORTHO = "o"
    P_ISOMETRIC = "i"
    P_PERSPECTIVE = "p"
    P_EGO = "e"

    PROJECTIONS = (
        P_TOP,
        P_ORTHO,
        P_ISOMETRIC,
        P_PERSPECTIVE,
        P_EGO,
    )

    def __init__(self, width, height, projection=P_TOP):
        self.projection = projection
        self.width = width
        self.height = height

        self.user_transformation = None

        self._zoom = 0.
        self._rotation = glm.vec3(0)
        self._mat_project = glm.mat4(1)
        self._mat_transform = glm.mat4(1)

        self._szoom = 0.
        self._srotation = glm.vec3(0)
        self._smat_project = glm.mat4(1)
        self._smat_transform = glm.mat4(1)

        self.init()

    def __str__(self):
        return "Projection('%s', %sx%s)" % (self.projection, self.width, self.height)

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
        return self._smat_project * self._smat_transform

    @property
    def projection_matrix(self):
        return self._smat_project

    @property
    def inverse_projection_matrix(self):
        return glm.inverse(self._smat_project)

    @property
    def transformation_matrix(self):
        return self._smat_transform

    @property
    def near(self):
        return self._near

    @property
    def far(self):
        return self._far

    def is_perspective(self):
        return self.projection in "pe"

    def get_direction(self, dir):
        """Transforms vec3 direction to a direction matching the current transformation"""
        dir = glm.inverse(self.transformation_matrix) * glm.vec4(dir, 0)
        return glm.vec3(dir)

    def init(self, projection=None):
        if projection is not None:
            self.projection = projection

        if self.projection in "oit":
            self._near = -30
            self._far = 100
        else:
            self._near = 0.01
            self._far = 100

        self._init_rotation()
        self._calc_matrix()

    def update(self, dt):
        d = min(1, dt)
        self._szoom += d + (self._zoom - self._szoom)
        self._srotation += d * (self._rotation - self._srotation)

        self._calc_matrix()

        d = min(1, dt * 25)
        self._smat_project += d * (self._mat_project - self._smat_project)
        self._smat_transform += d * (self._mat_transform - self._smat_transform)

    def get_depth_mask_values(self):
        if self.projection in "iot":
            return 0.25, .25
        return .999, .002

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

    def _init_rotation(self):
        self._rotation = glm.vec3(0)
        if self.projection=="o":
            self._rotation[0] = -glm.pi()/4
        if self.projection in "ep":
            self._rotation[0] = -glm.pi()/2.
        if self.projection == "i":
            self._rotation[0] = -glm.pi()/3.3
            self._rotation[2] = glm.pi()/4.

    def _calc_matrix(self):
        sc = 11
        asp = self.width / self.height

        # projection

        if self.projection in "it":
            ysc = sc/asp
            proj = glm.ortho(-sc,sc, -ysc,ysc, self._near, self._far)
        elif self.projection == "o":
            ysc = sc/asp * .75
            proj = glm.ortho(-sc,sc, -ysc,ysc, self._near, self._far)
        elif self.projection == "p":
            proj = glm.perspectiveFov(1., self.width, self.height, self._near, self._far)
            proj = glm.translate(proj, glm.vec3(0, 0, -5))
        else:  # "e"
            proj = glm.perspectiveFov(2., self.width, self.height, self._near, self._far)

        self._mat_project = proj

        # transformation
        
        trans = glm.rotate(glm.mat4(1), self._srotation[0], glm.vec3(1,0,0))
        trans = glm.rotate(trans, self._srotation[1], glm.vec3(0,1,0))
        trans = glm.rotate(trans, self._srotation[2], glm.vec3(0,0,1))
        trans = glm.translate(trans, glm.vec3(0, 0, [-3,-2,-4,-1,0]["oipet".index(self.projection)]))

        trans = glm.scale(trans, glm.vec3(max(0.01, 1.+self.zoom/10.)))

        if self.user_transformation is not None:
            trans = trans * self.user_transformation

        self._mat_transform = trans


