import numpy as np
import json
import os


class Sweep(object):
    """
    Parameters
    ----------
    path : str
        Full path to a directory containing at least a data.dat and a meta.json
        file.

    Attributes
    ----------
    data : numpy structured array
        Contains the data from data.dat with names given by the columns key in
        meta.json.
    meta : dictionary
        Contains meta.json as a dictionary.

    Notes
    -----
    This class currently supports loading data with a dimension of 1 or 2.
    """
    def __init__(self, path):
        self.path = path
        self.load()
        self.dimension = get_dimension(self.meta)
        if self.dimension == 2:
            self.get2d()
        elif self.dimension > 2:
            err_str = 'Data dimensions higher than 2 are not supported.'
            raise RuntimeError(err_str)

    def load(self):
        (self.data, self.meta) = load_dir(self.path)

    def get2d(self):
        (data, meta) = (self.data, self.meta)
        c1, c2 = data.dtype.names[:2]
        (self.data, self.meta) = reshape2d(data[c1], data[c2], data), meta


def load_dir(path, meta_only=False):
    with open(os.path.join(path, 'meta.json')) as f:
        meta = json.load(f)
    if meta_only:
        return meta
    columns = meta['columns']
    dtype = [(x['name'], float) for x in columns]
    with open(os.path.join(path, 'data.dat')) as f:
        def content():
            for line in f:
                if line.strip():
                    yield tuple(float(x) for x in line.split())
        data = np.fromiter(content(), dtype=dtype)
    return (data, meta)

def reshape2d(column1, column2, column3):
    different_from_first = (column1 != column1[0]).nonzero()[0]
    if len(different_from_first) == 0:
        raise RuntimeError('every value in column1 is identical')
    else:
        sweep_length = different_from_first[0]
    if sweep_length == 1:
        raise RuntimeError('the first two value in column 1 are unequal')
    number_of_sweeps = len(column1) // sweep_length
    number_of_good_points = number_of_sweeps * sweep_length
    return np.reshape(
        column3[:number_of_good_points],
        (number_of_sweeps, sweep_length)
    ).transpose()

def get_dimension(meta):
    dimension = 0
    valid_types = ('Sweep', 'sweep', 'Repeat', 'Forever', 'Line', 'Timed')
    def recurse_jobs(job, dimension):
        if job['type'] in valid_types:
            dimension += 1
        try:
            return recurse_jobs(job['job'], dimension)
        except KeyError:
            return dimension
    return recurse_jobs(meta['job'], dimension)
