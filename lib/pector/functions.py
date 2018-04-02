from . import tools


def dot(v1, v2):
    """
    Dot product of self and other vec3
    :param arg: float sequence of length 3
    :return: float

    >>> dot((1,2,3), (4,5,6)) # (1*4)+(2*5)+(3*6)
    32.0
    """
    tools.check_float_sequence(v1)
    tools.check_float_sequence(v2, len(v1))
    return sum([x * float(v2[i]) for i, x in enumerate(v1)])




if __name__ == "__main__":
    import doctest
    doctest.testmod()
