import numpy as np
from numpy import nanmin, nanmax


class Handler3Ddata(object):
    def __init__(self, x_data, y_data, z_data):
        self.data = [None] * 3
        self.data[0] = x_data
        self.data[1] = y_data
        self.data[2] = z_data
        self.x_extent = None
        self.y_extent = None
        self.z_extent = None
        self.data_is_valid = True
        if z_data is None:
            self.set_invalid()
            return
        self.set_data_for_imshow()

    def set_data_for_imshow(self):
        data = self.data
        z_data_dim = len(data[2].shape)
        if z_data_dim != 2:
            self.set_invalid()
            return
        col0_axis = self.arr_varies_monotonically_on_axis(data[0])
        col1_axis = self.arr_varies_monotonically_on_axis(data[1])
        if not set((col0_axis, col1_axis)) == set((0, 1)):
            self.set_invalid()
            return
        col0_lims = [data[0][0,0], data[0][-1,-1]]
        col1_lims = [data[1][0,0], data[1][-1,-1]]
        if col0_axis == 0:
            data_for_imshow = np.transpose(data[2])
        else:
            data_for_imshow = data[2]
        if col0_lims[0] > col0_lims[1]:
            col0_lims.reverse()
            data_for_imshow = np.fliplr(data_for_imshow)
        if col1_lims[0] > col1_lims[1]:
            col1_lims.reverse()
            data_for_imshow = np.flipud(data_for_imshow)
        self.data_for_imshow = data_for_imshow
        self.x_extent = col0_lims
        self.y_extent = col1_lims
        self.z_extent = [nanmin(data_for_imshow), nanmax(data_for_imshow)]
        self.extent = col0_lims + col1_lims

    def get_data(self):
        return self.data_for_imshow

    def get_extent(self):
        return self.extent

    def set_invalid(self):
        self.data_is_valid = False
        self.data_for_imshow = None
        self.extent = None

    def get_x_extent(self):
        return self.x_extent

    def get_y_extent(self):
        return self.y_extent

    def get_z_extent(self):
        return self.z_extent

    @staticmethod
    def arr_varies_monotonically_on_axis(arr):
        for axis in (0,1):
            idx = [0,0]
            idx[axis] = slice(None)
            candidate = arr[idx]
            arr_diff = np.diff(candidate)
            # Check that there are non-zero elements in arr_diff.
            # Otherwise arr is constant.
            if not any(arr_diff):
                continue
            # Check that the elements are the same,
            # i.e., the slope of arr is constant.
            if not np.allclose(arr_diff, arr_diff[0]):
                continue
            # Check that arr consists solely of copies of candidate.
            # First, insert an np.newaxis in candidate so you can subtract it
            # from arr.
            if axis == 0:
                candidate = candidate[...,np.newaxis]
            if not np.allclose(arr, candidate):
                continue
            return axis
        return -1
