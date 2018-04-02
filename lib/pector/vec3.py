import math
from . import vec_base, tools, const

class vec3(vec_base):
    """
    Class vec3 implementation.
    It behaves like a list of floats of length 3
    Arguments to member functions can be any list-like objects,
    containing float-convertible elements,
    typically of length 3 as well.
    """

    def __unicode__(self):
        return "vec3(%g, %g, %g)" % (self.v[0], self.v[1], self.v[2])

    # ---- x,y,z properties ----

    @property
    def x(self):
        return self.v[0]
    @x.setter
    def x(self, arg):
        self.v[0] = float(arg)

    @property
    def y(self):
        return self.v[1]
    @y.setter
    def y(self, arg):
        self.v[1] = float(arg)

    @property
    def z(self):
        return self.v[2]
    @z.setter
    def z(self, arg):
        self.v[2] = float(arg)

    # --- list-like ---

    def __len__(self):
        return 3

    # ------- getter -------

    def get_rotation_to(self, new_dir, fallback=None):
        """
        Returns a quaternion with the rotation
        needed to align this vector with new_dir.
        :param new_dir: float sequence of length 3, must be normalized
        :return: quat
        """
        from .quat import quat
        v0 = self.normalized_safe()
        d = v0.dot(new_dir)
        if d >= .999999:
            return quat()
        elif d < -0.999999:
            if fallback:
                return quat(fallback, 180.)
            else:
                ax = vec3(1,0,0).cross(v0)
                if ax.length_squared() < 0.00001:
                    ax = vec3(0,1,0).cross(v0)
                ax.normalize()
                return quat(ax, 180.)
        else:
            s = math.sqrt((1.+d) * 2.)
            invs = 1. / s
            c = v0.cross(new_dir)
            return quat(c.x * invs, c.y * invs, c.z * invs, s * .5).normalized()


    # ------ inplace methods -------

    def cross(self, arg3):
        """
        Makes this vector the cross-product of this and arg3, INPLACE
        The cross product is always perpendicular to the plane described by the two vectors
        :param arg3: float sequence of length 3
        :return: self
        >>> vec3((1,0,0)).cross((0,1,0))
        vec3(0, 0, 1)
        >>> vec3((1,0,0)).cross((0,0,1))
        vec3(0, -1, 0)
        >>> vec3((0,1,0)).cross((0,0,1))
        vec3(1, 0, 0)
        """
        tools.check_float_sequence(arg3)
        x = self.y * arg3[2] - self.z * arg3[1]
        y = self.z * arg3[0] - self.x * arg3[2]
        self.z = self.x * arg3[1] - self.y * arg3[0]
        self.x = x
        self.y = y
        return self

    def reflect(self, norm):
        """
        Reflects this vector on a plane with given normal, INPLACE
        :param norm: float sequence of length 3
        :return: self
        Example: suppose ray coming from top-left, going down on a flat plane
        >>> vec3(2,-1,0).reflect((0,1,0)).round()
        vec3(2, 1, 0)
        """
        tools.check_float_sequence(norm, 3)
        self.set(self - vec3(norm) * self.dot(norm) * 2.)
        return self

    def rotate_x(self, degree):
        """
        Rotates this vector around the x-axis, INPLACE
        :param degree: the degrees [0., 360.]
        :return: self
        >>> vec3((1,2,3)).rotate_x(90).round()
        vec3(1, -3, 2)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        y = self.y * ca - self.z * sa
        self.z = self.y * sa + self.z * ca
        self.y = y
        return self

    def rotate_y(self, degree):
        """
        Rotates this vector around the y-axis, INPLACE
        :param degree: the degrees [0., 360.]
        :return: self
        >>> vec3((1,2,3)).rotate_y(90).round()
        vec3(3, 2, -1)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        x = self.x * ca + self.z * sa
        self.z = -self.x * sa + self.z * ca
        self.x = x
        return self

    def rotate_z(self, degree):
        """
        Rotates this vector around the z-axis, INPLACE
        :param degree: the degrees [0., 360.]
        :return: self
        >>> vec3((1,2,3)).rotate_z(90).round()
        vec3(-2, 1, 3)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        x = self.x * ca - self.y * sa
        self.y = self.x * sa + self.y * ca
        self.x = x
        return self

    def rotate_axis(self, axis, degree):
        """
        Rotates this vector around an arbitrary axis, INPLACE
        :param axis: float sequence of length 3
        :param degree: the degrees [0., 360.]
        :return: self
        >>> vec3((1,2,3)).rotate_axis((1,0,0), 90) == vec3((1,2,3)).rotate_x(90)
        True
        """
        tools.check_float_sequence(axis, 3)
        degree *= const.DEG_TO_TWO_PI
        si = math.sin(degree)
        co = math.cos(degree)

        m = axis[0] * axis[0]+ axis[1] * axis[1] + axis[2] * axis[2]
        ms = math.sqrt(m)

        x = (axis[0] * (axis[0] * self.x + axis[1] * self.y + axis[2] * self.z)
            + co * (self.x * (axis[1] * axis[1] + axis[2] * axis[2]) + axis[0] * (-axis[1] * self.y - axis[2] * self.z))
            + si * ms * (-axis[2] * self.y + axis[1] * self.z)) / m
        y = (axis[1] * (axis[0] * self.x + axis[1] * self.y + axis[2] * self.z)
            + co * (self.y * (axis[0] * axis[0] + axis[2] * axis[2]) + axis[1] * (-axis[0] * self.x - axis[2] * self.z))
            + si * ms * (axis[2] * self.x - axis[0] * self.z)) / m
        self.z = (axis[2] * (axis[0] * self.x + axis[1] * self.y + axis[2] * self.z)
            + co * (self.z * (axis[0] * axis[0] + axis[1] * axis[1]) + axis[2] * (-axis[0] * self.x - axis[1] * self.y))
            + si * ms * (-axis[1] * self.x + axis[0] * self.y)) / m
        self.x = x
        self.y = y
        return self

    # --- value-copying methods ---

    def crossed(self, arg3):
        """
        Returns the cross-product of this vector and arg3
        The cross product is always perpendicular to the plane described by the two vectors
        :param arg3: float sequence of length 3
        :return: self
        >>> vec3((1,0,0)).crossed((0,1,0))
        vec3(0, 0, 1)
        >>> vec3((1,0,0)).crossed((0,0,1))
        vec3(0, -1, 0)
        >>> vec3((0,1,0)).crossed((0,0,1))
        vec3(1, 0, 0)
        """
        return self.copy().cross(arg3)

    def reflected(self, norm):
        """
        Returns the this vector reflected on a plane with given normal
        :param norm: float sequence of length 3
        :return: self
        Example: suppose ray coming from top-left, going down on a flat plane
        >>> vec3((2,-1,0)).reflected((0,1,0)).rounded()
        vec3(2, 1, 0)
        """
        return self.copy().reflect(norm)

    def rotated_x(self, degree):
        """
        Returns this vector rotated around the x-axis
        :param degree: the degrees [0., 360.]
        :return: vec3
        >>> vec3((1,2,3)).rotated_x(90).rounded()
        vec3(1, -3, 2)
        """
        return self.copy().rotate_x(degree)

    def rotated_y(self, degree):
        """
        Returns this vector rotated around the y-axis
        :param degree: the degrees [0., 360.]
        :return: vec3
        >>> vec3((1,2,3)).rotated_y(90).rounded()
        vec3(3, 2, -1)
        """
        return self.copy().rotate_y(degree)

    def rotated_z(self, degree):
        """
        Returns this vector rotated around the z-axis
        :param degree: the degrees [0., 360.]
        :return: vec3
        >>> vec3((1,2,3)).rotated_z(90).rounded()
        vec3(-2, 1, 3)
        """
        return self.copy().rotate_z(degree)

    def rotated_axis(self, axis, degree):
        """
        Returns this vector rotated around an arbitrary axis
        :param axis: float sequence of length 3
        :param degree: the degrees [0., 360.]
        :return: vec3
        >>> vec3(1,2,3).rotated_axis((1,0,0), 90) == vec3(1,2,3).rotated_x(90)
        True
        """
        return self.copy().rotate_axis(axis, degree)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
