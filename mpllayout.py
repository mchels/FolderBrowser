from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from plotcontrols import PlotControls
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import copy
import matplotlib.colors as mcolors


class MplLayout(QtWidgets.QWidget):
    """
    Contains canvas, toolbar and a PlotControls object.
    """
    def __init__(self, statusBar=None):
        super(MplLayout, self).__init__()
        fig = Figure()
        fig.add_subplot(1, 1, 1)
        self.statusBar = statusBar
        self.fig_canvas = FigureCanvasQTAgg(fig)
        self.fig_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.comboBoxes = PlotControls(self.update_sel_cols, self.update_cmap, self.update_lims, self.copy_fig_to_clipboard)
        self.navi_toolbar = NavigationToolbar2QT(self.fig_canvas, self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.navi_toolbar)
        layout.addWidget(self.fig_canvas)
        layout.addWidget(self.comboBoxes)
        self.setLayout(layout)
        self.none_str = '---'
        self.sel_col_names = self.comboBoxes.get_sel_texts()
        self.cbar = None
        self.image = None
        self.cmaps = ['Reds', 'Blues_r', 'symmetric']
        # Set default colormap.
        self.cmap = 'Reds'
        self.cmap_name = 'Reds'
        self.lims = [None] * 3
        self.update_is_scheduled = False

    def reset_and_plot(self, sweep=None):
        if sweep is not None:
            self.sweep = sweep
        raw_col_names = list(self.sweep.data.dtype.names)
        pcol_names = self.sweep.pdata.get_names()
        all_names = raw_col_names + pcol_names
        col3_names = all_names + [self.none_str]
        col_names = [all_names, all_names, col3_names]
        self.comboBoxes.reset(col_names)
        self.update_sel_cols()

    def update_sel_cols(self, new_num=None):
        """
        To maintain a consistent state we must update the plot at the end.
        """
        self.prev_sel_col_names = self.sel_col_names
        self.sel_col_names = self.comboBoxes.get_sel_texts()
        # Try to make 1D plot if '---' is selected in the third comboBox.
        self.plot_is_2D = self.sel_col_names[2] != self.none_str
        self.data_is_1D = self.sweep.dimension == 1
        plot_is_invalid = self.plot_is_2D and self.data_is_1D
        if plot_is_invalid:
            if self.statusBar is not None:
                msg = "You can't do an image plot, since the data is only 1D."
                self.statusBar.showMessage(msg, 2000)
            self.comboBoxes.set_text_on_box(2, self.none_str)
        self.update_is_scheduled = True
        self.set_data_for_plot()
        self.set_labels()
        self.update_lims()
        self.update_plot()

    def set_data_for_plot(self):
        n_dims = 3
        self.plot_data = [None] * n_dims
        for i in range(n_dims):
            col_name = self.sel_col_names[i]
            if col_name == self.none_str:
                continue
            try:
                self.plot_data[i] = self.sweep.data[col_name]
            except ValueError:
                self.plot_data[i] = self.sweep.pdata[col_name]
        self.set_data_for_imshow()

    def set_data_for_imshow(self):
        if self.plot_data[2] is None:
            return
        col0_axis = arr_varies_monotonically_on_axis(self.plot_data[0])
        col1_axis = arr_varies_monotonically_on_axis(self.plot_data[1])
        if not set((col0_axis, col1_axis)) == set((0, 1)):
            msg = 'Selected columns not valid for image plot. No action taken.'
            self.sel_col_names = self.prev_sel_col_names
            self.statusBar.showMessage(msg, 1000)
            return
        col0_lims = [self.plot_data[0][0,0], self.plot_data[0][-1,-1]]
        col1_lims = [self.plot_data[1][0,0], self.plot_data[1][-1,-1]]
        if col0_axis == 0:
            data_for_imshow = np.transpose(self.plot_data[2])
        else:
            data_for_imshow = self.plot_data[2]
        if col0_lims[0] > col0_lims[1]:
            col0_lims.reverse()
            data_for_imshow = np.fliplr(data_for_imshow)
        if col1_lims[0] > col1_lims[1]:
            col1_lims.reverse()
            data_for_imshow = np.flipud(data_for_imshow)
        self.data_for_imshow = data_for_imshow
        self.extent = col0_lims + col1_lims
        
    def set_labels(self):
        self.labels = [None] * 3
        for i in range(3):
            col_name = self.sel_col_names[i]
            if col_name == self.none_str:
                continue
            self.labels[i] = self.sweep.get_label(col_name)

    def update_lims(self):
        """
        user_lims are limits set by user in the lim_boxes.
        extent is data limits for both 1D and 2D plots.
        """
        user_lims = [None] * 3
        ext = [None] * 3
        for i, lim_box in enumerate(self.comboBoxes.lim_boxes):
            user_lims[i] = self.parse_lims(lim_box.text())
        if self.plot_is_2D:
            ext[0] = self.extent[0:2]
            ext[1] = self.extent[2:4]
            ext[2] = [self.data_for_imshow.min(), self.data_for_imshow.max()]
        else:
            ext[0] = [self.plot_data[0].min(), self.plot_data[0].max()]
            ext[1] = [self.plot_data[1].min(), self.plot_data[1].max()]
        for i in (0,1,2):
            self.lims[i] = self.combine_lim_lists(user_lims[i], ext[i])
        self.update_cmap()
        if not self.update_is_scheduled:
            self.update_plot()

    def update_cmap(self, cmap_name=None):
        """
        cmap_name: string corresponding to a built-in matplotlib colormap
              OR 'symmetric' which is defined below.
        """
        if not self.plot_is_2D:
            return
        if type(cmap_name) is int:
            cmap_name = self.cmaps[cmap_name]
        if cmap_name is None:
            cmap_name = self.cmap_name
        self.cmap_name = cmap_name
        if cmap_name == 'symmetric':
            z_lims = self.lims[2]
            max_abs = np.max(np.abs(z_lims))
            min_val = z_lims[0]
            max_val = z_lims[1]
            if min_val <= 0 <= max_val:
                z_range = max_val - min_val
                n_neg_points = int(abs(min_val)/z_range*100)
                neg_low_limit = 0.5 - abs(min_val)/max_abs/2
                neg_vals = np.linspace(neg_low_limit, 0.5, n_neg_points)
                neg_colors = plt.cm.RdBu_r(neg_vals)
                n_pos_points = int(max_val/z_range*100)
                pos_high_limit = 0.5 + max_val/max_abs/2
                pos_vals = np.linspace(0.5, pos_high_limit, n_pos_points)
                pos_colors = plt.cm.RdBu_r(pos_vals)
                colors = np.vstack((neg_colors, pos_colors))
                cmap = mcolors.LinearSegmentedColormap.from_list('foo', colors)
                self.cmap = cmap
            elif 0 <= min_val <= max_val:
                self.cmap = plt.get_cmap('Reds')
            elif min_val <= max_val <= 0:
                self.cmap = plt.get_cmap('Blues')
        else:
            self.cmap = plt.get_cmap(cmap_name)
        if not self.update_is_scheduled:
            self.update_plot()

    def update_plot(self):
        if self.plot_is_2D: self.update_2D_plot()
        else: self.update_1D_plot()

    def update_1D_plot(self):
        if self.cbar is not None:
            self.cbar.remove()
            self.cbar = None
            self.image = None
        for ax in self.fig_canvas.figure.get_axes():
            ax.cla()
            ax.plot(self.plot_data[0], self.plot_data[1])
            ax.autoscale_view(True, True, True)
        self.common_plot_update()

    def update_2D_plot(self):
        fig = self.fig_canvas.figure
        ax = fig.get_axes()[0]
        try:
            self.image.set_data(self.data_for_imshow)
            self.image.set_extent(self.extent)
        except AttributeError as error:
            ax.cla()
            self.image = ax.imshow(
                self.data_for_imshow,
                aspect='auto',
                cmap=self.cmap,
                interpolation='none',
                origin='lower',
                extent=self.extent,
            )
            self.cbar = fig.colorbar(mappable=self.image)
        self.image.set_cmap(self.cmap)
        self.cbar.set_label(self.labels[2])
        self.image.set_clim(self.lims[2])
        self.cbar.draw_all()
        ax.autoscale_view(True, True, True)
        self.common_plot_update()

    def common_plot_update(self):
        self.update_is_scheduled = False
        ax = self.fig_canvas.figure.get_axes()[0]
        ax.relim()
        ax.set_xlabel(self.labels[0])
        ax.set_ylabel(self.labels[1])
        ax.set_xlim(self.lims[0])
        ax.set_ylim(self.lims[1])
        ax.set_title(self.sweep.meta['name'], fontsize=10)
        self.custom_tight_layout()
        self.fig_canvas.draw()

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

    def copy_fig_to_clipboard(self):
        image = QtWidgets.QWidget.grab(self.fig_canvas).toImage()
        QtWidgets.QApplication.clipboard().setImage(image)

    def parse_lims(self, text):
        lims = text.split(':')
        if len(lims) != 2:
            return (None, None)
        lower_lim = self.conv_to_float_or_None(lims[0])
        upper_lim = self.conv_to_float_or_None(lims[1])
        return (lower_lim, upper_lim)

    @staticmethod
    def conv_to_float_or_None(str):
        try:
            return float(str)
        except ValueError:
            return None

    @staticmethod
    def combine_lim_lists(list1, list2):
        if list1 is None or list2 is None:
            return None
        assert len(list1) == len(list2)
        out_list = [None] * len(list1)
        for i in range(len(list1)):
            if list1[i] is None:
                out_list[i] = list2[i]
            else:
                out_list[i] = list1[i]
        return out_list


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
