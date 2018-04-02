import math
from . import tools, const, mat_base, vec3


class mat4(mat_base):
    """
    4x4 anisotropic matrix - column-major order
    """

    def __len__(self):
        return 16

    def num_rows(self):
        return 4

    # ----- public API getter ------

    def position(self):
        """
        Return translational (the last column) part as vec3
        :return: vec3
        >>> mat4().translated((2,3,4)).position()
        vec3(2, 3, 4)
        """
        return vec3(self.v[12:15])

    # ---- public API setter -----

    def inverse_simple(self):
        """
        Inverts a uniformly-scaled, non-skewed matrix, INPLACE
        :return: self
        """
        self.v = self.inversed_simple().v
        return self

    def set_position(self, arg3):
        """
        Sets the translation-part of the matrix which is the last column
        :param arg3: a float sequence of length 3
        :return: self
        >>> mat4().set_position((2,3,4))
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 2,3,4,1)
        """
        tools.check_float_sequence(arg3, 3)
        self.v[12] = float(arg3[0])
        self.v[13] = float(arg3[1])
        self.v[14] = float(arg3[2])
        return self

    def set_translate(self, arg3):
        """
        Initializes the matrix with a translation transform, INPLACE
        :param arg3: a float sequence of lengh 3
        :return: self
        >>> mat4(1).set_translate((2,3,4))
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 2,3,4,1)
        """
        tools.check_float_sequence(arg3, 3)
        self.set_identity()
        self.v[12] = float(arg3[0])
        self.v[13] = float(arg3[1])
        self.v[14] = float(arg3[2])
        return self

    def set_rotate_x(self, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param degree: degrees of rotation
        :return: self
        >>> mat4().set_rotate_x(90).round()
        mat4(1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,0,0,1)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        self.set_identity()
        self.v[5] = ca
        self.v[6] = sa
        self.v[9] = -sa
        self.v[10] = ca
        return self

    def set_rotate_y(self, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param degree: degrees of rotation
        :return: self
        >>> mat4().set_rotate_y(90).round()
        mat4(0,0,-1,0, 0,1,0,0, 1,0,0,0, 0,0,0,1)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        self.set_identity()
        self.v[0] = ca
        self.v[2] = -sa
        self.v[8] = sa
        self.v[10] = ca
        return self

    def set_rotate_z(self, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param degree: degrees of rotation
        :return: self
        >>> mat4().set_rotate_z(90).round()
        mat4(0,1,0,0, -1,0,0,0, 0,0,1,0, 0,0,0,1)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        self.set_identity()
        self.v[0] = ca
        self.v[1] = sa
        self.v[4] = -sa
        self.v[5] = ca
        return self

    def set_rotate_axis(self, axis, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param axis: float sequence of length 3, must be normalized!
        :param degree: degrees of rotation
        :return: self
        >>> mat4().set_rotate_axis((1,0,0), 90).round()
        mat4(1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,0,0,1)
        """
        tools.check_float_sequence(axis, 3)
        degree *= const.DEG_TO_TWO_PI
        si = math.sin(degree)
        co = math.cos(degree)
        m = 1. - co

        self.set_identity()
        self.v[0] =  co + axis[0] * axis[0] * m
        self.v[5] =  co + axis[1] * axis[1] * m
        self.v[10] = co + axis[2] * axis[2] * m

        t1 = axis[0] * axis[1] * m
        t2 = axis[2] * si
        self.v[1] = t1 + t2
        self.v[4] = t1 - t2

        t1 = axis[0] * axis[2] * m
        t2 = axis[1] * si
        self.v[2] = t1 - t2
        self.v[8] = t1 + t2

        t1 = axis[1] * axis[2] * m
        t2 = axis[0] * si
        self.v[6] = t1 + t2
        self.v[9] = t1 - t2
        return self


    def translate(self, arg3):
        """
        Adds a translation to the current matrix, INPLACE
        :param arg3: float sequence of length 3
        :return: self
        >>> mat4().translate((1,2,3))
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 1,2,3,1)
        """
        m = mat4().set_translate(arg3)
        self._multiply_inplace(m)
        return self

    def rotate_x(self, degree):
        """
        Adds a rotation to the current matrix, INPLACE
        :param degree: angle of rotation in degree
        :return: self
        >>> mat4().rotate_x(90).round()
        mat4(1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,0,0,1)
        """
        m = mat4().set_rotate_x(degree)
        self._multiply_inplace(m)
        return self

    def rotate_y(self, degree):
        """
        Adds a rotation to the current matrix, INPLACE
        :param degree: angle of rotation in degree
        :return: self
        >>> mat4().rotate_y(90).round()
        mat4(0,0,-1,0, 0,1,0,0, 1,0,0,0, 0,0,0,1)
        """
        m = mat4().set_rotate_y(degree)
        self._multiply_inplace(m)
        return self

    def rotate_z(self, degree):
        """
        Adds a rotation to the current matrix, INPLACE
        :param degree: angle of rotation in degree
        :return: self
        >>> mat4().rotate_z(90).round()
        mat4(0,1,0,0, -1,0,0,0, 0,0,1,0, 0,0,0,1)
        """
        m = mat4().set_rotate_z(degree)
        self._multiply_inplace(m)
        return self

    def rotate_axis(self, axis, degree):
        """
        Adds a rotation to the current matrix, INPLACE
        :param axis: axis of rotation, must be normalized
        :param degree: angle of rotation in degree
        :return: self
        >>> mat4().rotate_axis((1,0,0), 90).round()
        mat4(1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,0,0,1)
        """
        m = mat4().set_rotate_axis(axis, degree)
        self._multiply_inplace(m)
        return self

    def reflect(self, normal):
        self.v[0:3] = vec3(self.v[0:3]).reflect(normal)
        self.v[4:7] = vec3(self.v[4:7]).reflect(normal)
        self.v[8:11] = vec3(self.v[8:11]).reflect(normal)
        return self

    # ------ value-copying methods -------

    def transposed(self):
        """
        Returns a mat4 with columns and rows interchanged
        :return: mat4
        >>> mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)).transposed()
        mat4(1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)
        """
        return self.copy().transpose()

    def inversed_simple(self):
        """
        Returns inverse of a uniformly-scaled, non-skewed matrix.
        :return: mat4
        """
        m = mat4()
        m.v[0] = self.v[0]
        m.v[1] = self.v[4]
        m.v[2] = self.v[8]
        m.v[3] = self.v[3]

        m.v[4] = self.v[1]
        m.v[5] = self.v[5]
        m.v[6] = self.v[9]
        m.v[7] = self.v[7]

        m.v[8] = self.v[2]
        m.v[9] = self.v[6]
        m.v[10] = self.v[10]
        m.v[11] = self.v[11]

        m.v[12] = -(self.v[12] * self.v[0]) - (self.v[13] * self.v[1]) - (self.v[14] * self.v[2])
        m.v[13] = -(self.v[12] * self.v[4]) - (self.v[13] * self.v[5]) - (self.v[14] * self.v[6])
        m.v[14] = -(self.v[12] * self.v[8]) - (self.v[13] * self.v[9]) - (self.v[14] * self.v[10])
        m.v[15] = self.v[15]
        return m

    def position_cleared(self):
        """
        Returns a copy of the matrix with translation set to zero
        :return: mat4
        """
        return self.copy().set_position((0, 0, 0))

    def translated(self, arg3):
        """
        Returns a translated matrix
        :param arg3: float sequence of length 3
        :return: mat4
        >>> mat4().translated((1,2,3))
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 1,2,3,1)
        """
        return self.copy().translate(arg3)

    def rotated_x(self, degree):
        """
        Returns a rotated matrix
        :param degree: angle of rotation in degree
        :return: mat4
        >>> mat4().rotated_x(90).rounded()
        mat4(1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,0,0,1)
        """
        return self.copy().rotate_x(degree)

    def rotated_y(self, degree):
        """
        Returns a rotated matrix
        :param degree: angle of rotation in degree
        :return: mat4
        >>> mat4().rotated_y(90).rounded()
        mat4(0,0,-1,0, 0,1,0,0, 1,0,0,0, 0,0,0,1)
        """
        return self.copy().rotate_y(degree)

    def rotated_z(self, degree):
        """
        Returns a rotated matrix
        :param degree: angle of rotation in degree
        :return: mat4
        >>> mat4().rotated_z(90).rounded()
        mat4(0,1,0,0, -1,0,0,0, 0,0,1,0, 0,0,0,1)
        """
        return self.copy().rotate_z(degree)

    def rotated_axis(self, axis, degree):
        """
        Returns a rotated matrix
        :param axis: axis of rotation, must be normalized
        :param degree: angle of rotation in degree
        :return: mat4
        >>> mat4().rotated_axis((1,0,0), 90).rounded()
        mat4(1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,0,0,1)
        """
        return self.copy().rotate_axis(axis, degree)


if __name__ == "__main__":
    import doctest
    doctest.testmod()