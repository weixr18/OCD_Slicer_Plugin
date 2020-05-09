# python2.7
# Contributors: Xinran Wei,
import numpy as np


def arrayInterpolation(Array, space):
    """Linear Interpolation of the array"""
    if space <= 1:
        raise ValueError(
            "ValueError: parameter 'space' should have value greater than 1.")

    Array = np.array(Array)
    shape = Array.shape

    height = (shape[0] - 1) * space
    ret = np.zeros([height, shape[1], shape[2]])

    for i in range(height):
        if i % space == 0:
            ret[i] = Array[i // space]
        else:
            offset = i - (i // space) * space
            ret[i] = offset * Array[i // space] + \
                (space - offset) * Array[i // space + 1]

            ret[i] = ret[i] / space

    return ret
