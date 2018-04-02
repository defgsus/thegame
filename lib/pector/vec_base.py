import math
from . import tools, const

"""
Abstract base class for vectors and matrices"""


class vec_base:
    """
    Vector/Matrix base class.
    It behaves like a list of floats
    Arguments to member functions can be any list-like objects,
    containing float-convertible elements,
    typically of same size as self.
    """

    def __init__(self, *arg):
        if not arg:
            self.v = [0. for i in range(len(self))]
            return
        self.set(*arg)

    def __unicode__(self):
        return "vec_base(len=%d)" % len(self)

    def __repr__(self):
        return self.__unicode__()

    # --- list-like ---

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        return self.v.__iter__()

    def __getitem__(self, item):
        return self.v[item]

    def __setitem__(self, key, value):
        self.v[key] = float(value)

    def __contains__(self, item):
        return item in self.v

    # --- boolean equality ---

    def __eq__(self, other):
        """
        Compares the vector with another vector or number.
        :param other:
        :return:
        >>> vec3(1,2,3) == vec3(1,2,3)
        True
        >>> vec3() == mat4()
        False
        >>> vec3(1,1,1) == 1
        True
        """
        if tools.is_number(other):
            for i in range(len(self)):
                if not self.v[i] == other:
                    return False
            return True
        tools.check_float_sequence(other)
        if not len(other) == len(self):
            return False
        for i in range(len(self)):
            if not self.v[i] == other[i]:
                return False
        return True

    ## --- classic math ops ---

    def __abs__(self):
        return self.__class__([abs(x) for x in self.v])

    def __neg__(self):
        return self.__class__([-x for x in self.v])

    def __round__(self, n=None):
        if n is None:
            return self.__class__([float(round(x)) for x in self.v])
        else:
            return self.__class__([float(round(x, n)) for x in self.v])

    # ------- arithmetic ops --------

    def __add__(self, arg):
        return self._binary_operator(arg, lambda l, r: l + r)

    def __radd__(self, arg):
        return self._binary_operator(arg, lambda r, l: l + r)

    def __iadd__(self, arg):
        return self._binary_operator_inplace(arg, lambda l, r: l + r)


    def __sub__(self, arg):
        return self._binary_operator(arg, lambda l, r: l - r)

    def __rsub__(self, arg):
        return self._binary_operator(arg, lambda r, l: l - r)

    def __isub__(self, arg):
        return self._binary_operator_inplace(arg, lambda l, r: l - r)


    def __mul__(self, arg):
        return self._binary_operator(arg, lambda l, r: l * r)

    def __rmul__(self, arg):
        return self._binary_operator(arg, lambda r, l: l * r)

    def __imul__(self, arg):
        return self._binary_operator_inplace(arg, lambda l, r: l * r)


    def __truediv__(self, arg):
        return self._binary_operator(arg, lambda l, r: l / r)

    def __rtruediv__(self, arg):
        return self._binary_operator(arg, lambda r, l: l / r)

    def __itruediv__(self, arg):
        return self._binary_operator_inplace(arg, lambda l, r: l / r)


    def __mod__(self, arg):
        return self._binary_operator(arg, lambda l, r: l % r)

    def __rmod__(self, arg):
        return self._binary_operator(arg, lambda r, l: l % r)

    def __imod__(self, arg):
        return self._binary_operator_inplace(arg, lambda l, r: l % r)

    # --- op helper ---

    def _binary_operator(self, arg, op):
        if tools.is_number(arg):
            fother = float(arg)
            return self.__class__([op(x, fother) for x in self.v])
        tools.check_float_sequence(arg, len(self))
        return self.__class__([op(x, float(arg[i])) for i, x in enumerate(self.v)])

    def _binary_operator_inplace(self, arg, op):
        if tools.is_number(arg):
            fother = float(arg)
            for i in range(len(self)):
                self.v[i] = op(self.v[i], fother)
            return self
        tools.check_float_sequence(arg, len(self))
        for i in range(len(self)):
            self.v[i] = op(self.v[i], float(arg[i]))
        return self

    # --- public API ---

    def set(self, *arg):
        """
        Set the values of this vector
        :param arg: a single float to set all components equally, 
        or a mixture of floats and float sequences
        :return: self
        """
        if len(arg) == 1:
            if tools.is_number(arg[0]):
                arg = float(arg[0])
                self.v = [arg for i in range(len(self))]
                return self

            if tools.is_float_sequence(arg[0]):
                o = arg[0]
                # mat4 -> mat3
                if len(o) == 16 and len(self) == 9:
                    self.v = [o[0], o[1], o[2],  o[4], o[5], o[6],  o[8], o[9], o[10]]
                    return self
                # mat3 -> mat4
                if len(o) == 9 and len(self) == 16:
                    self.v = [o[0], o[1], o[2], 0., o[3], o[4], o[5], 0., 
                              o[6], o[7], o[8], 0., 0.,0.,0.,1.]
                    return self

        self.v = [0. for i in range(len(self))]
        num_copied = 0
        i = 0
        while num_copied < len(self) and i < len(arg):
            a = arg[i]
            if tools.is_number(a):
                self.v[num_copied] = float(a)
                num_copied += 1
                i += 1
            elif tools.is_float_sequence(a):
                for j in a:
                    if num_copied >= len(self):
                        raise ValueError("Too much data to initialize %s" % self.__class__.__name__)
                    self.v[num_copied] = float(j)
                    num_copied += 1
                i += 1
            else:
                raise TypeError("Invalid argument %s to %s" % (type(a), self.__class__.__name__))
        if i < len(arg):
            raise ValueError("Too much data to initialize %s " % self.__class__.__name__)

    def copy(self):
        """
        Returns a new instance of the vector
        """
        return self.__class__(self.v)

    # ----- getter -----

    def length(self):
        """
        Returns cartesian length of vector
        :return: float
        >>> vec3((5,0,0)).length()
        5.0
        >>> vec3(1).length() == math.sqrt(3.)
        True
        """
        return math.sqrt(sum([x*x for x in self.v]))

    def length_squared(self):
        """
        Returns the square of the cartesian length of vector
        :return: float
        >>> vec3((5,0,0)).length_squared()
        25.0
        >>> vec3(1).length_squared()
        3.0
        """
        return sum([x*x for x in self.v])

    def distance(self, arg3):
        """
        Returns the cartesian distance between self and other vector
        :param arg3: float sequence of length 3
        :return: float
        >>> vec3((5,0,0)).distance(vec3(0))
        5.0
        >>> vec3(1).distance(vec3(2)) == math.sqrt(3)
        True
        """
        return math.sqrt(sum([(x-arg3[i])*(x-arg3[i]) for i, x in enumerate(self.v)]))

    def distance_squared(self, arg3):
        """
        Returns the square of the cartesian distance between self and other vector
        :param arg3: float sequence of length 3
        :return: float
        >>> vec3((5,0,0)).distance_squared(vec3(0))
        25.0
        >>> vec3(1).distance_squared(vec3(2))
        3.0
        """
        return sum([(x-arg3[i])*(x-arg3[i]) for i, x in enumerate(self.v)])

    def dot(self, arg):
        """
        Returns the dot product of self and other vec3
        :param arg3: float sequence of length 3
        :return: float
        >>> vec3((1,2,3)).dot((4,5,6)) # (1*4)+(2*5)+(3*6)
        32.0
        """
        tools.check_float_sequence(arg, len(self))
        return sum([x * float(arg[i]) for i, x in enumerate(self.v)])


    # ------ inplace methods -------

    def floor(self):
        """
        Applies the floor() function to all elements, INPLACE
        :return: self
        >>> vec3((0.1, 1.5, 2.9)).floor()
        vec3(0, 1, 2)
        >>> vec3((-1.1, -1.9, -0.9)).floor()
        vec3(-2, -2, -1)
        >>> mat4((.1,.2,.3,.4, .5,.6,.7,.8, .9,1.,1.1,1.2, 1.3,1.4,1.5,1.6)).floor()
        mat4(0,0,0,0, 0,0,0,0, 0,1,1,1, 1,1,1,1)
        >>> mat4((-.1,-.2,-.3,-.4, -.5,-.6,-.7,-.8, -.9,-1.,-1.1,-1.2, -1.3,-1.4,-1.5,-1.6)).floor()
        mat4(-1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-2,-2, -2,-2,-2,-2)
        """
        self.v = [math.floor(x) for x in self.v]
        return self

    def round(self, ndigits=None):
        """
        Applies the round() function to all elements, INPLACE
        :param ndigits: None, or the number of digits
        :return: self
        >>> vec3((0.1, 1.5, 2.9)).round()
        vec3(0, 2, 3)
        >>> vec3((-1.1, -1.9, -0.9)).round()
        vec3(-1, -2, -1)
        >>> vec3((0.123, 0.4999, 0.5102)).round(2)
        vec3(0.12, 0.5, 0.51)
        >>> mat4((.1,.2,.3,.4, .5,.6,.7,.8, .9,1.,1.1,1.2, 1.3,1.4,1.5,1.6)).round()
        mat4(0,0,0,0, 0,1,1,1, 1,1,1,1, 1,1,2,2)
        >>> mat4((-.1,-.2,-.3,-.4, -.5,-.6,-.7,-.8, -.9,-1.,-1.1,-1.2, -1.3,-1.4,-1.5,-1.6)).round()
        mat4(0,0,0,0, 0,-1,-1,-1, -1,-1,-1,-1, -1,-1,-2,-2)
        """
        if ndigits:
            self.v = [round(x,ndigits) for x in self.v]
        else:
            self.v = [round(x) for x in self.v]
        return self

    def normalize(self):
        """
        Normalizes the vector, e.g. makes it length 1, INPLACE
        :return: self
        >>> vec3((1,1,0)).normalize()
        vec3(0.707107, 0.707107, 0)
        >>> vec3((1,2,3)).normalize().length() == 1
        True
        """
        l = self.length()
        self.v = [x / l for x in self.v]
        return self

    def normalize_safe(self):
        """
        Normalizes the vector, e.g. makes it length 1, INPLACE
        If the length is zero, this call does nothing
        :return: self
        >>> vec3((1,1,0)).normalize_safe()
        vec3(0.707107, 0.707107, 0)
        >>> vec3(0).normalize_safe()
        vec3(0, 0, 0)
        """
        l = self.length()
        if not l == 0.:
            self.v = [x / l for x in self.v]
        return self

    def lerp(self, other, t):
        """
        Linear interpolation to other
        :param other: sequence of floats
        :param t: float, 0. - 1.
        :return: self
        """
        tools.check_float_sequence(other, len(self))
        for i in range(len(self)):
            self.v[i] += t * (other[i] - self.v[i])
        return self

    # --- value-copying methods ---

    def floored(self):
        """
        Returns a vector with the floor() function applied to all elements
        :return: new vector
        >>> vec3((0.1, 1.5, 2.9)).floored()
        vec3(0, 1, 2)
        >>> vec3((-1.1, -1.9, -0.9)).floored()
        vec3(-2, -2, -1)
        """
        return self.copy().floor()

    def rounded(self, ndigits=None):
        """
        Returns a vector with round() applied to all elements
        :param ndigits: None, or the number of digits
        :return: new vector
        >>> vec3((0.1, 1.5, 2.9)).rounded()
        vec3(0, 2, 3)
        >>> vec3((-1.1, -1.9, -0.9)).rounded()
        vec3(-1, -2, -1)
        >>> vec3((0.123, 0.4999, 0.5102)).rounded(2)
        vec3(0.12, 0.5, 0.51)
        """
        return self.copy().round(ndigits)

    def normalized(self):
        """
        Returns normalized vector, e.g. makes it length 1.
        :return: new vector
        >>> vec3((1,1,0)).normalized()
        vec3(0.707107, 0.707107, 0)
        >>> vec3((1,2,3)).normalized().length() == 1
        True
        """
        return self.copy().normalize()

    def normalized_safe(self):
        """
        Returns normalized vector, e.g. makes it length 1.
        Does nothing if length is 0.
        :return: new vector
        >>> vec3((1,1,0)).normalized_safe()
        vec3(0.707107, 0.707107, 0)
        >>> vec3(0).normalized_safe()
        vec3(0, 0, 0)
        """
        return self.copy().normalize_safe()

