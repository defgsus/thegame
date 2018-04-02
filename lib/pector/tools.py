
def is_number(arg):
    """Return True when arg is convertible to float, False otherwise"""
    try:
        float(arg)
        return True
    except:
        return False

def is_float_sequence(arg):
    if isinstance(arg, dict):
        return False
    try:
        for i in arg:
            float(i)
        return True
    except:
        return False

def check_float_number(arg):
    try:
        return float(arg)
    except:
        raise TypeError("Expected float, got %s" % type(arg))


def check_float_sequence(arg, expect_len=None):
    # see if sequence
    try:
        l = len(arg)
    except:
        raise TypeError("Expected sequence, got %s" % type(arg))
    # check length
    if expect_len is not None and not len(arg) == expect_len:
        raise TypeError("Expected sequence of length %d, but %s has length %d" % (expect_len, type(arg), len(arg)))
    # check convertible to float
    try:
        for i in arg:
            float(i)
    except:
        raise TypeError("Expected sequence of floats, got %s - %s" % (type(arg), str(arg)))
