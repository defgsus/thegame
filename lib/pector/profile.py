from .vec3 import vec3
import random

def rnd_vec3(mi=-1., ma=1.):
    return vec3((random.uniform(mi, ma),
                 random.uniform(mi, ma),
                 random.uniform(mi, ma)))

def nbody_case(nbodies, nframes):
    pos = [rnd_vec3() for i in range(nbodies)]
    imp = [rnd_vec3() for i in range(nbodies)]

    for it in range(nframes):
        for i in range(len(pos)):
            for j in range(i+1, len(pos)):
                d = (pos[j] - pos[i])
                l = d.length()
                d /= l
                a = 0.02 * l * d
                imp[i] += a
                imp[j] -= a
        for i in range(len(pos)):
            pos[i] += imp[i]
            imp[i] *= 0.99


# TODO: i get
#   File "/usr/lib/python3.4/cProfile.py", line 22, in <module>
#     run.__doc__ = _pyprofile.run.__doc__
#   AttributeError: 'module' object has no attribute 'run'
# without these:
def run(): pass
def runctx(): pass

if __name__ == "__main__":

    def print_stats(prof):
        stats = sorted(prof.getstats(), key=lambda t: -t[3]/t[1])
        fmt = "%10s | %20s | %s"
        print(fmt % ("time", "time per M calls", "name"))
        for pe in stats:
            print(fmt % (str(round(pe[3],8)), str(pe[3]/pe[1]*1.e+6), pe[0]))

    def do_profile(code):
        print("------ %s ------" % code)
        import cProfile
        prof = cProfile.Profile()
        prof.run(code)
        print_stats(prof)


    do_profile("nbody_case(nbodies=32, nframes=50)")


"""
------ nbody_case(nbodies=32, nframes=50) ------
      time |     time per M calls | name
  1.293539 |            1293539.0 | <built-in method exec>
  1.293508 |   1293507.9999999998 | <code object <module> at 0x7ff78da22ed0, file "<string>", line 1>
  1.293499 |            1293499.0 | <code object nbody_case at 0x7ff78d9f34b0, file "/home/defgsus/prog/python/dev/pector/pector/profile.py", line 9>
  0.000322 |   321.99999999999994 | <code object <listcomp> at 0x7ff78d9f3390, file "/home/defgsus/prog/python/dev/pector/pector/profile.py", line 10>
  0.000255 |   254.99999999999997 | <code object <listcomp> at 0x7ff78d9f3420, file "/home/defgsus/prog/python/dev/pector/pector/profile.py", line 11>
   0.36807 |   14.841532258064516 | <code object __sub__ at 0x7ff78d9fe930, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 102>
  0.566942 |   11.430282258064516 | <code object _binary_operator at 0x7ff78da01780, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 143>
   0.22724 |    9.162903225806451 | <code object __rmul__ at 0x7ff78d9fedb0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 115>
  0.239938 |    9.088560606060605 | <code object __iadd__ at 0x7ff78d9fe810, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 98>
  0.216015 |    8.710282258064517 | <code object __isub__ at 0x7ff78d9feb70, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 108>
  0.000554 |              8.65625 | <code object rnd_vec3 at 0x7ff78da6cf60, file "/home/defgsus/prog/python/dev/pector/pector/profile.py", line 4>
  0.520338 |    6.705386597938144 | <code object _binary_operator_inplace at 0x7ff78da01810, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 150>
  0.279042 |    5.618596971649485 | <code object __init__ at 0x7ff78d9f38a0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 11>
  0.259388 |    5.222857603092784 | <code object set at 0x7ff78da019c0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 163>
   0.09277 |   3.7407258064516125 | <code object __itruediv__ at 0x7ff78da01270, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 128>
  0.005101 |   3.1881249999999994 | <code object __imul__ at 0x7ff78d9feed0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 118>
  0.073217 |   2.9522983870967736 | <code object <listcomp> at 0x7ff78da016f0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 148>
   0.05166 |   2.0830645161290318 | <code object length at 0x7ff78da01ae0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 196>
  0.207934 |    1.654682327476445 | <code object check_float_sequence at 0x7ff78da0c1e0, file "/home/defgsus/prog/python/dev/pector/pector/tools.py", line 18>
  0.030468 |   1.2285483870967742 | <code object <listcomp> at 0x7ff78da01660, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 146>
  0.166587 |   0.9418932060792473 | <code object is_number at 0x7ff78da0c0c0, file "/home/defgsus/prog/python/dev/pector/pector/tools.py", line 2>
   0.02533 |   0.5100273840206185 | <code object <listcomp> at 0x7ff78da018a0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 187>
  0.011345 |   0.4574596774193548 | <built-in method sum>
   0.01087 |   0.4383064516129032 | <code object <listcomp> at 0x7ff78da01a50, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 205>
   8.2e-05 |  0.42708333333333337 | <code object uniform at 0x7ff78da0c930, file "/usr/lib/python3.4/random.py", line 342>
  0.022075 |   0.2904605263157894 | <code object __iter__ at 0x7ff78d9f3e40, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 51>
   0.15862 |   0.2854828839854577 | <built-in method len>
  0.006613 |   0.2666532258064516 | <built-in method sqrt>
  0.031618 |  0.13867543859649123 | <code object __getitem__ at 0x7ff78d9f3ed0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 54>
  0.010909 |    0.137739898989899 | <code object <lambda> at 0x7ff78d9fe780, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 99>
  0.010068 |  0.13532258064516126 | <code object <lambda> at 0x7ff78da011e0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 129>
  0.009718 |  0.13061827956989247 | <code object <lambda> at 0x7ff78d9feae0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 109>
  0.009641 |  0.12958333333333336 | <code object <lambda> at 0x7ff78d9fe8a0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 103>
  0.009471 |   0.1272983870967742 | <code object <lambda> at 0x7ff78d9fed20, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 116>
  0.000546 |  0.11374999999999998 | <code object <lambda> at 0x7ff78d9fee40, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 119>
   1.5e-05 |             0.078125 | <method 'random' of '_random.Random' objects>
   0.03102 |  0.07660621147463252 | <code object __len__ at 0x7ff78d9f3db0, file "/home/defgsus/prog/python/dev/pector/pector/vec3.py", line 48>
       0.0 |                  0.0 | <method 'disable' of '_lsprof.Profiler' objects>
"""