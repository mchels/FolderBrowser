import numpy as np
from numpy import nanmin, nanmax


class DataHandler(object):
    """
    -DONE Verify input.
    -DONE Determine whether data is 1D or 2D.
    -DONE Set very large or small values to nan.
    -DONE Investigate whether data are linspaces.
    -DONE Sort and flip data that is linspace.
    -DONE Determine whether data is suitable for imshow. imshow_eligible
    """
    def __init__(self, x, y):
        self.clip_min = -1e25
        self.clip_max = 1e25
        self.x = x
        self.y = y
        self.data = [self.x, self.y]
        self.data_is_valid = False

    def set_data_validity(self):
        """
        Depends on
        self.data
        self.data_dim
        """
        data_is_valid = True
        try:
            for data in self.data:
                assert data.ndim == self.data_dim
                assert data.shape == self.data[0].shape
        except Exception:
            data_is_valid = False
        self.data_is_valid = data_is_valid

    def clip_tdata_to_nan(self):
        for tdata in self.tdata:
            if tdata is None:
                continue
            tdata = self.clip_to_nan(tdata, self.clip_min, self.clip_max)

    def get_extent_of_data_dim(self, dim):
        """
        Depends on _set_tdata
        """
        assert dim in range(self.n_data_arrs)
        arr = self.tdata[dim]
        return [nanmin(arr), nanmax(arr)]

    @staticmethod
    def clip_to_nan(arr, clip_min, clip_max):
        assert type(arr) is np.ndarray
        # By default Numpy gives a RuntimeWarning when a nan is generated. We
        # are explicitly generating nans here so we don't want to see the
        # warning.
        with np.errstate(invalid='ignore'):
            arr[arr < clip_min] = np.nan
            arr[arr > clip_max] = np.nan
        return arr

    @staticmethod
    def is_linear(arr):
        """
        'linear' in this context also implies 'not constant'.
        """
        assert arr.ndim == 1
        arr_diff = np.diff(arr)
        # Check that there are non-zero elements in arr_diff.
        # Otherwise arr is constant.
        if not any(arr_diff):
            return False
        # Check that the elements are the same,
        # i.e., the slope of arr is constant.
        if not np.allclose(arr_diff, arr_diff[0], atol=1e-15):
            return False
        return True

    def is_linear_on_axis(self, arr):
        assert arr.ndim == 2
        for axis in (0,1):
            idx = [0,0]
            idx[axis] = slice(None)
            arr_1D = arr[idx]
            if not self.is_linear(arr_1D):
                continue
            # Check that arr consists solely of copies of arr_1D. First,
            # insert an np.newaxis in arr_1D so you can subtract it from arr.
            if axis == 0:
                arr_1D = arr_1D[...,np.newaxis]
            if not np.allclose(arr, arr_1D):
                continue
            return axis
        return False

    @staticmethod
    def reverse_axis(arr, axis):
        assert axis in range(arr.ndim)
        idx = [slice(None)] * arr.ndim
        idx[axis] = slice(None, None, -1)
        return arr[idx]


class Transformed2DData(DataHandler):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.n_data_arrs = len(self.data)
        self.data_dim = 1
        self.imshow_eligible = False
        self.set_data_validity()
        if not self.data_is_valid:
            return
        self._set_data_is_linear()
        self._set_tdata()
        self.clip_tdata_to_nan()

    def _set_data_is_linear(self):
        data_is_linear = [False] * self.n_data_arrs
        for i, data in enumerate(self.data):
            data_is_linear[i] = self.is_linear(data)
        self.data_is_linear = data_is_linear

    def _set_tdata(self):
        tdata = np.copy(self.data)
        for i, arr in enumerate(tdata):
            if not self.data_is_linear[i]:
                continue
            if arr[0] > arr[-1]:
                # We can sort the array by simply reversing the elements
                # because we know it is linearly increasing or decreasing
                # monotonously from self.data_is_linear.
                arr = self.reverse_axis(arr, 0)
        self.tdata = tdata


class Transformed3DData(DataHandler):
    def __init__(self, x, y, z):
        super().__init__(x, y)
        if z is not None:
            self.data.append(z)
        self.n_data_arrs = len(self.data)
        self.data_dim = 2
        self.set_data_validity()
        if not self.data_is_valid:
            return
        self._set_data_is_linear()
        self._set_imshow_eligible()
        self._set_tdata()
        self.clip_tdata_to_nan()

    def _set_data_is_linear(self):
        data_is_linear = [False] * self.n_data_arrs
        lin_axis_for_data = [None] * self.n_data_arrs
        for i, data in enumerate(self.data):
            axis = self.is_linear_on_axis(data)
            if axis is False:
                continue
            data_is_linear[i] = True
            lin_axis_for_data[i] = axis
        self.data_is_linear = data_is_linear
        self.lin_axis_for_data = lin_axis_for_data

    def _set_imshow_eligible(self):
        """
        Depends on
        - _set_data_is_linear
        """
        imshow_eligible = False
        # If x and y vary on axes 0 and 1 or vice versa the data is eligible
        # for imshow.
        lin_axes = [ax for ax in self.lin_axis_for_data if ax is not None]
        if sorted(lin_axes) == [0, 1]:
            imshow_eligible = True
        self.imshow_eligible = imshow_eligible

    def _set_tdata(self):
        """
        Depends on
        - _set_data_is_linear
        Must run before
        - clip_tdata_to_nan
        """
        lin_axes = [ax for ax in self.lin_axis_for_data if ax is not None]
        if lin_axes == [0, 1]:
            tdata = [arr.copy().T for arr in self.data]
        else:
            tdata = [arr.copy() for arr in self.data]
        tdata_lin_axes = [1, 0]
        # Sort tdata along dimensions where the x and y arrays vary linearly.
        for i in (0, 1):
            arr = tdata[i]
            if not self.data_is_linear[i]:
                continue
            if arr[0,0] > arr[-1,-1]:
                lin_axis = tdata_lin_axes[i]
                # We can sort the array by simply reversing the elements
                # because we know it is linearly increasing or decreasing
                # monotonously from self.data_is_linear.
                arr = self.reverse_axis(arr, lin_axis)
                if self.n_data_arrs == 3:
                    self.tdata[2] = self.reverse_axis(self.tdata[2], lin_axis)
        self.tdata = tdata


def data_handler_factory(x, y, z=None):
    dim = try_get_arr_dim(x, y, z)
    assert dim in (1, 2, None)
    if dim == 1:
        assert z is None
        return Transformed2DData(x, y)
    elif dim == 2:
        return Transformed3DData(x, y, z)
    elif dim is None:
        return DataHandler()

def try_get_arr_dim(*args):
    for arr in args:
        try:
            return arr.ndim
        except AttributeError:
            pass
    return None
