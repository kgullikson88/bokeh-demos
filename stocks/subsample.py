import numpy as np
import dask.array as da

def coarsen(reduction, x, factor):
    """

    >>> x = np.arange(10)
    >>> coarsen(np.max, x, 2)
    array([1, 3, 5, 7, 9])

    >>> coarsen(np.min, x, 5)
    array([0, 5])
    """
    axis = {0: factor, 1: factor}
    # Ensure that shape is divisible by coarsening factor
    slops = [-(d % factor) for d in x.shape]
    slops = [slop or None for slop in slops]
    x = x[tuple(slice(0, slop) for slop in slops)]
 
    if isinstance(x, np.ndarray):
        return da.chunk.coarsen(reduction, x, axis)
    if isinstance(x, da.Array):
        return da.coarsen(reduction, x, axis)
    raise NotImplementedError()
