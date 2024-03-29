"""
Code is from https://pvigier.github.io/2018/06/13/perlin-noise-numpy.html
(https://github.com/pvigier/perlin-numpy/blob/master/perlin_numpy/perlin2d.py)
"""
from typing import Tuple, Callable, Optional

import numpy as np


def interpolate_linear(t):
    return t


def interpolate_poly2(t):
    return t*(3. - 2. * t)


def interpolate_poly5(t):
    return t*t*t*(t*(t*6 - 15) + 10)


def generate_perlin_noise_2d(
        shape: Tuple[int, int],
        res: Tuple[int, int],
        tileable: Tuple[bool, bool] = (False, False),
        interpolant: Callable[[np.ndarray], np.ndarray] = interpolate_poly5,
        rng: Optional[np.random.Generator] = None,
        values: Optional[np.ndarray] = None,
):
    """Generate a 2D numpy array of perlin noise.
    Args:
        shape: The shape of the generated array (tuple of two ints).
            This must be a multple of res.
        res: The number of periods of noise to generate along each
            axis (tuple of two ints). Note shape must be a multiple of
            res.
        tileable: If the noise should be tileable along each axis
            (tuple of two bools). Defaults to (False, False).
        interpolant: The interpolation function, defaults to
            t*t*t*(t*(t*6 - 15) + 10).
        rng: optional numpy.random.Generator to use
        values: optional ndarray with initial random values,
            defaults to rng.random([res[0] + 1, res[1] + 1])
    Returns:
        A numpy array of shape shape with the generated noise.
    Raises:
        ValueError: If shape is not a multiple of res.
    """
    if rng is None:
        rng = np.random
    if values is None:
        values = rng.random([res[0]+1, res[1]+1])
    else:
        assert values.shape == (res[0]+1, res[1]+1), \
            f"expected {(res[0]+1, res[1]+1)}, got {values.shape}"

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]] \
               .transpose(1, 2, 0) % 1
    # Gradients
    angles = 2*np.pi*values
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    if tileable[0]:
        gradients[-1,:] = gradients[0,:]
    if tileable[1]:
        gradients[:,-1] = gradients[:,0]
    gradients = gradients.repeat(d[0], 0).repeat(d[1], 1)
    g00 = gradients[    :-d[0],    :-d[1]]
    g10 = gradients[d[0]:     ,    :-d[1]]
    g01 = gradients[    :-d[0],d[1]:     ]
    g11 = gradients[d[0]:     ,d[1]:     ]
    # Ramps
    n00 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]  )) * g00, 2)
    n10 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]  )) * g10, 2)
    n01 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]-1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]-1)) * g11, 2)
    # Interpolation
    t = interpolant(grid)
    n0 = n00*(1-t[:,:,0]) + t[:,:,0]*n10
    n1 = n01*(1-t[:,:,0]) + t[:,:,0]*n11
    return np.sqrt(2)*((1-t[:,:,1])*n0 + t[:,:,1]*n1)
