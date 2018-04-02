import math
from . import vec_base, tools, const

class vec2(vec_base):
    """
    Class vec2 implementation.
    It behaves like a list of floats of length 2
    Arguments to member functions can be any list-like objects,
    containing float-convertible elements,
    typically of length 2 as well.
    """

    def __unicode__(self):
        return "vec2(%g, %g)" % (self.v[0], self.v[1])

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

    # --- list-like ---

    def __len__(self):
        return 2

    # ------ inplace methods -------

    def reflect(self, norm):
        """
        Reflects this vector on a line with given normal, INPLACE
        :param norm: float sequence of length 2
        :return: self
        Example: suppose ray coming from top-left, going down on a planar surface
        >>> vec2(2,-1).reflect((0,1)).round()
        vec2(2, 1)
        """
        tools.check_float_sequence(norm, 2)
        self.set(self - vec3(norm) * self.dot(norm) * 2.)
        return self

    def rotate_z(self, degree):
        """
        Rotates this vector around the z-axis, INPLACE
        :param degree: the degrees [0., 360.]
        :return: self
        >>> vec2((1,2)).rotate_z(90).round()
        vec3(-2, 1)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        x = self.x * ca - self.y * sa
        self.y = self.x * sa + self.y * ca
        self.x = x
        return self


    # --- value-copying methods ---

    def reflected(self, norm):
        """
        Returns the this vector reflected on a plane with given normal
        :param norm: float sequence of length 2
        :return: self
        Example: suppose ray coming from top-left, going down on a flat plane
        >>> vec3(2,-1).reflected((0,1)).rounded()
        vec3(2, 1)
        """
        return self.copy().reflect(norm)

    def rotated_z(self, degree):
        """
        Returns this vector rotated around the z-axis
        :param degree: the degrees [0., 360.]
        :return: vec2
        >>> vec2((1,2)).rotated_z(90).rounded()
        vec3(-2, 1)
        """
        return self.copy().rotate_z(degree)



if __name__ == "__main__":
    import doctest
    doctest.testmod()
