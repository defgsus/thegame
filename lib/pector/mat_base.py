# import math
from . import tools, vec_base, vec3


class mat_base(vec_base):
    """
    Base class for common matrix operations
    """
    def __init__(self, *arg):
        self.set(*arg)

    def __unicode__(self):
        r = "%s(" % self.__class__.__name__
        for i, x in enumerate(self.v):
            r += "%g" % x
            if i < len(self)-1:
                r += ","
                if i % self.num_rows() == self.num_rows()-1:
                    r += " "
        return r + ")"

    def num_rows(self):
        raise NotImplementedError

    def as_list_list(self, row_major=False):
        """
        Returns the matrix as list of lists
        :param row_major: If true, ordering will be row-major, otherwise native column-major
        :return: list of lists
        >>> mat3(1,2,3,4,5,6,7,8,9).as_list_list()
        [[1,2,3], [4,5,6], [7,8,9]]
        >>> mat3(1,2,3,4,5,6,7,8,9).as_list_list(row_major=True)
        [[1,4,7], [2,5,8], [3,6,9]]
        """
        ret = []
        if not row_major:
            for c in range(self.num_rows()):
                ret.append(self.v[c*self.num_rows():(c+1)*self.num_rows()])
        else:
            for c in range(self.num_rows()):
                ret.append([self.v[c+r*self.num_rows()] for r in range(self.num_rows())])

        return ret

    # ------- arithmetic ops --------

    def __mul__(self, arg):
        if tools.is_number(arg):
            return self._binary_operator(arg, lambda l, r: l * r)
        tools.check_float_sequence(arg)
        return self._multiply(self, arg)

    def __rmul__(self, arg):
        if tools.is_number(arg):
            return self._binary_operator(arg, lambda r, l: l * r)
        tools.check_float_sequence(arg)
        return self._multiply(arg, self)

    def __imul__(self, arg):
        if tools.is_number(arg):
            return self._binary_operator_inplace(arg, lambda l, r: l * r)
        tools.check_float_sequence(arg, len(self))
        return self._multiply_inplace(arg)

    # --- helper ---

    def _multiply(self, l, r):
        """One big multiply implementation for all derived types
        The code should be spread to the derived classes
        but it was convenient to write it all in one place"""
        from .quat import quat
        # mat * mat
        if len(l) == len(self) == len(r):
            m = self.__class__(l)
            m._multiply_inplace(r)
            return m
        elif isinstance(r, quat):
            # mat3 * quat
            if len(l) == 9:
                return l * r.as_mat3()
            # mat4 * quat
            elif len(l) == 16:
                return l * r.as_mat4()
            else:
                raise TypeError("Can not multiply %s and quat" % (type(l)))
        # mat4 * vec3
        elif len(l) == 16 and len(r) == 3:
            return vec3.vec3(
                l[0] * r[0] + l[4] * r[1] + l[8 ] * r[2] + l[12],
                l[1] * r[0] + l[5] * r[1] + l[9 ] * r[2] + l[13],
                l[2] * r[0] + l[6] * r[1] + l[10] * r[2] + l[14] )
        # mat3 * vec3
        elif len(l) == 9 and len(r) == 3:
            return vec3.vec3(
                l[0] * r[0] + l[3] * r[1] + l[6] * r[2] ,
                l[1] * r[0] + l[4] * r[1] + l[7] * r[2] ,
                l[2] * r[0] + l[5] * r[1] + l[8] * r[2] )
        else:
            raise TypeError("Can not matrix-multiply %s (%d) with %s (%d)" % (
                                type(l), len(l), type(r), len(r) ))

    def _multiply_inplace(self, m):
        sv = list(self.v)
        for row in range(self.num_rows()):
            for col in range(self.num_rows()):
                s = 0.
                for i in range(self.num_rows()):
                    s += sv[row + i * self.num_rows()] * m.v[i + col * self.num_rows()]
                self.v[row + col * self.num_rows()] = s
        return self

    # ----- public API getter ------

    def get(self, row, column):
        """
        Returns the element at given row and column
        :return: float
        """
        return self.v[column * self.num_rows() + row]

    def trace(self):
        """
        Returns the sum of the diagonal
        :return: float
        """
        return sum(self.v[::self.num_rows()+1])

    def has_translation(self):
        """
        Returns True if the matrix contains a translation, False otherwise
        :return: bool
        """
        return len(self) == 16 and not (self.v[12] == 0. and self.v[13] == 0. and self.v[14] == 0.)

    def has_rotation(self):
        """
        Returns True if the matrix contains a rotation or skew transform, False otherwise
        :return: bool
        """
        num = min(3, self.num_rows())
        for r in range(num):
            for c in range(num):
                if not r == c and not self.v[c*self.num_rows()+r] == 0:
                    return True
        return False

    # ---- public API setter -----

    def set_identity(self, value=1.):
        """
        Sets the identity matrix
        :param value: The identity value, default = 1.
        :return: self
        >>> mat4().set_identity()
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)
        >>> mat4().set_identity(2)
        mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,2)
        """
        arg = tools.check_float_number(value)
        self.v = [arg if i % (self.num_rows()+1) == 0 else 0. for i in range(len(self))]
        return self

    def set(self, *arg):
        """
        Sets the content of the matrix
        :param arg: either a single float to set the identity,
        or a mixture of floats and float sequences
        :return: self
        >>> mat4().set(1)
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)
        >>> mat4().set(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)
        mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)
        >>> mat4().set((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16))
        mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)
        >>> mat3().set(vec3(1), (2,3,4), 5,(6,7,))
        mat3(1,1,1, 2,3,4, 5,6,7)
        """
        if arg and len(arg) == 1 and tools.is_number(arg[0]):
            self.set_identity(float(arg[0]))
            return self
        if not arg:
            self.set_identity(1.)
            return self
        return super(mat_base, self).set(*arg)

    def transpose(self):
        """
        Exchanges the matrix columns and rows, INPLACE
        :return: self
        >>> mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)).transpose()
        mat4(1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)
        """
        self.v = [self.v[row + i*self.num_rows()] for row in range(self.num_rows()) for i in range(self.num_rows())]
        return self

    def init_scale(self, arg):
        """
        Initializes the matrix with a scale transform, INPLACE
        :param arg: either a float or a float sequence of length 3
        :return: self
        >>> mat4().init_scale(2)
        mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,1)
        >>> mat4().init_scale((2,3,4))
        mat4(2,0,0,0, 0,3,0,0, 0,0,4,0, 0,0,0,1)
        """
        if tools.is_number(arg):
            self.set(arg)
            if self.num_rows() > 3:
                self.v[-1] = 1.
            return self
        num = self.num_rows()-1 if self.num_rows() > 3 else self.num_rows()
        tools.check_float_sequence(arg, num)
        self.set_identity()
        for i in range(num):
            self.v[i * (self.num_rows()+1)] = float(arg[i])
        return self


    def scale(self, arg):
        """
        Scales the current matrix, INPLACE
        :param arg3: single float or float sequence of length 3
        :return: self
        >>> mat4().scale(2)
        mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,1)
        >>> mat4().scale((2,3,4))
        mat4(2,0,0,0, 0,3,0,0, 0,0,4,0, 0,0,0,1)
        """
        m = self.__class__().init_scale(arg)
        self._multiply_inplace(m)
        return self


    # ------ value-copying methods -------

    def transposed(self):
        """
        Returns a mat4 with columns and rows interchanged
        :return: new matrix
        >>> mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)).transposed()
        mat4(1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)
        """
        return self.copy().transpose()

    def scaled(self, arg):
        """
        Returns a scaled matrix
        :param arg3: single float or float sequence of length 3
        :return: new matrix
        >>> mat4().scaled(2)
        mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,1)
        >>> mat4().scaled((2,3,4))
        mat4(2,0,0,0, 0,3,0,0, 0,0,4,0, 0,0,0,1)
        """
        return self.copy().scale(arg)
