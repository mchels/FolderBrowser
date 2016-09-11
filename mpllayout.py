from matplotlib.backends import qt_compat
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore
from customcomboboxes import CustomComboBoxes
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import copy


class MplLayout(QtGui.QWidget):
    """
    Contains canvas, toolbar and a customcomboboxes object.
    """
    def __init__(self, statusBar=None):
        super(MplLayout, self).__init__()
        fig = Figure()
        fig.add_subplot(1, 1, 1)
        self.statusBar = statusBar
        self.fig_canvas = FigureCanvasQTAgg(fig)
        self.comboBoxes = CustomComboBoxes(3, self.update_sel_cols, self.update_cmap, self.update_lims)
        self.navi_toolbar = NavigationToolbar2QT(self.fig_canvas, self)
        layout = QtGui.QGridLayout()
        n_rows_canvas = 3
        n_cols_canvas = 7
        for i, box in enumerate(self.comboBoxes.boxes):
            layout.addWidget(box, n_rows_canvas+1, i, 1, 1)
        layout.addWidget(self.comboBoxes.cmap_sel, n_rows_canvas+1, 3, 1, 1)
        for i, lim_box in enumerate(self.comboBoxes.lim_boxes):
            layout.addWidget(self.comboBoxes.lim_boxes[i], n_rows_canvas+1, i+4, 1, 1)
        layout.addWidget(self.fig_canvas, 1, 0, n_rows_canvas, n_cols_canvas)
        layout.addWidget(self.navi_toolbar, 0, 0, 1, n_cols_canvas)
        self.setLayout(layout)
        self.none_str = '---'
        self.sel_col_names = self.comboBoxes.get_sel_texts()
        self.cbar = None
        self.image = None
        self.cmaps = ['Reds', 'Blues_r', 'RdBu_r']
        # Set default colormap.
        self.cmap = 'Reds'
        self.lims = [None] * 3

    def update_sel_cols(self, new_num=None):
        """
        To maintain a consistent state we must update the plot at the end.
        """
        self.prev_sel_col_names = self.sel_col_names
        self.sel_col_names = self.comboBoxes.get_sel_texts()
        self.label_names = self.sel_col_names
        # Try to make 1D plot if '---' is selected in the third comboBox.
        self.plot_is_2D = self.sel_col_names[2] != self.none_str
        self.data_is_1D = self.sweep.dimension == 1
        plot_is_invalid = self.plot_is_2D and self.data_is_1D
        if plot_is_invalid:
            if self.statusBar is not None:
                msg = "You can't do an image plot, since the data is only 1D."
                self.statusBar.showMessage(msg, 2000)
            self.comboBoxes.set_text_on_box(2, self.none_str)
        self.update_plot()

    def reset_and_plot(self, sweep=None):
        if sweep is not None:
            self.sweep = sweep
        raw_cols = self.sweep.data.dtype.names
        col3_names = raw_cols + (self.none_str,)
        col_names = [raw_cols, raw_cols, col3_names]
        self.comboBoxes.reset(col_names)
        self.update_sel_cols()

    def update_plot(self):
        if self.plot_is_2D: self.update_2D_plot()
        else: self.update_1D_plot()

    def update_1D_plot(self):
        if self.cbar is not None:
            self.cbar.remove()
            self.cbar = None
            self.image = None
        plot_data = self.load_data_for_plot(dim=2)
        for ax in self.fig_canvas.figure.get_axes():
            ax.cla()
            ax.plot(plot_data[0], plot_data[1])
            ax.autoscale_view(True, True, True)
        self.common_plot_update()

    def update_2D_plot(self):
        plot_data = self.load_data_for_plot(dim=3)
        col0_axis = arr_varies_monotonically_on_axis(plot_data[0])
        col1_axis = arr_varies_monotonically_on_axis(plot_data[1])
        if not set((col0_axis, col1_axis)) == set((0, 1)):
            msg = 'Selected columns not valid for image plot. No action taken.'
            self.sel_col_names = self.prev_sel_col_names
            self.statusBar.showMessage(msg)
            return
        col0_lims = [plot_data[0][0,0], plot_data[0][-1,-1]]
        col1_lims = [plot_data[1][0,0], plot_data[1][-1,-1]]
        if col0_axis == 0:
            data_for_imshow = np.transpose(plot_data[2])
        else:
            data_for_imshow = plot_data[2]
        extent = col0_lims + col1_lims
        self.label_names = self.sel_col_names
        fig = self.fig_canvas.figure
        ax = fig.get_axes()[0]
        try:
            self.image.set_data(data_for_imshow)
            self.image.set_extent(extent)
            self.image.autoscale()
        except AttributeError as error:
            self.statusBar.showMessage('self.image does not exist')
            ax.cla()
            self.image = ax.imshow(
                data_for_imshow,
                aspect='auto',
                cmap=self.cmap,
                interpolation='none',
                origin='lower',
                extent=extent,
            )
            self.cbar = fig.colorbar(mappable=self.image)
            self.cbar.set_label(self.sel_col_names[2])
            self.clims = (np.min(data_for_imshow), np.max(data_for_imshow))
        ax.autoscale_view(True, True, True)
        self.common_plot_update()

    def common_plot_update(self):
        ax = self.fig_canvas.figure.get_axes()[0]
        ax.relim()
        ax.set_xlabel(self.label_names[0])
        ax.set_ylabel(self.label_names[1])
        if self.cbar is not None:
            self.cbar.set_label(self.label_names[2])
        ax.set_title(self.sweep.meta['name'], fontsize=10)
        self.custom_tight_layout()
        self.fig_canvas.figure.canvas.draw()

    def custom_tight_layout(self):
        # Sometimes we'll get an error:
        # ValueError: bottom cannot be >= top
        # This is a confirmed bug when using tight_layout():
        # https://github.com/matplotlib/matplotlib/issues/5456
        try:
            self.fig_canvas.figure.tight_layout()
        except ValueError:
            msg = ('Title is wider than figure.'
                   'This causes undesired behavior and is a known bug.')
            self.statusBar.showMessage(msg, 2000)

    def parse_lims(self, text):
        lims = text.split(':')
        if len(lims) != 2:
            return (None, None)
        lower_lim = self.conv_to_float_or_None(lims[0])
        upper_lim = self.conv_to_float_or_None(lims[1])
        return (lower_lim, upper_lim)

    def conv_to_float_or_None(self, str):
        try:
            return float(str)
        except ValueError:
            return None

    def update_lims(self):
        ax = self.fig_canvas.figure.get_axes()[0]
        for i, lim_box in enumerate(self.comboBoxes.lim_boxes):
            self.lims[i] = self.parse_lims(lim_box.text())
        if self.image is None:
            data_lims = ax.dataLim.get_points()
        elif self.image is not None:
            # data_lims = ax.viewLim.get_points()
            tmp = self.image.get_extent()
            data_lims = np.array([[tmp[0], tmp[2]], [tmp[1], tmp[3]]])
        user_lims = np.transpose([self.lims[0], self.lims[1]])
        new_lims = data_lims
        for i in (0,1):
            for j in (0,1):
                if user_lims[i][j] is not None:
                    new_lims[i][j] = user_lims[i][j]
        ax.set_xlim(new_lims[:,0])
        ax.set_ylim(new_lims[:,1])
        ax.relim()
        if self.image is None:
            ax.autoscale_view(True, True, True)
        elif self.image is not None:
            new_lims = copy.deepcopy(list(self.clims))
            user_lims = self.lims[2]
            for i in (0,1):
                if user_lims[i] is not None:
                    new_lims[i] = user_lims[i]
            self.image.set_clim(new_lims)
        self.custom_tight_layout()
        self.fig_canvas.figure.canvas.draw()

    def update_cmap(self, cmap):
        if self.image is not None:
            if type(cmap) is int:
                cmap = self.cmaps[cmap]
            self.image.set_cmap(cmap)
            self.cmap = cmap
            self.fig_canvas.figure.canvas.draw()

    def load_data_for_plot(self, dim):
        plot_data = [None] * dim
        for i in range(dim):
            plot_data[i] = self.sweep.data[self.sel_col_names[i]]
        return plot_data


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
