from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from plotcontrols import PlotControls
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import copy
import matplotlib.colors as mcolors


class MplLayout(QtWidgets.QWidget):
    """
    Contains canvas, toolbar and a PlotControls object.
    """
    def __init__(self, statusBar=None, parent=None):
        super(MplLayout, self).__init__()
        self.statusBar = statusBar
        self.parent = parent
        self.init_fig_and_canvas()
        self.cmap_names = ['Reds', 'Blues_r', 'symmetric']
        self.plotcontrols = PlotControls(self.update_sel_cols,
                                       self.update_cmap,
                                       self.update_lims,
                                       self.copy_fig_to_clipboard,
                                       self.cmap_names)
        self.init_navi_toolbar()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.navi_toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.plotcontrols)
        self.setLayout(layout)
        self.none_str = '---'
        self.sel_col_names = self.plotcontrols.get_sel_cols()
        self.cbar = None
        self.cmap_name = self.cmap_names[0]
        self.cmap = plt.get_cmap(self.cmap_name)
        self.lims = [None] * 3
        self.update_is_scheduled = False

    def reset_and_plot(self, sweep):
        self.sweep = sweep
        raw_col_names = list(self.sweep.data.dtype.names)
        pcol_names = self.sweep.pdata.get_names()
        all_names = raw_col_names + pcol_names
        col3_names = all_names + [self.none_str]
        col_names = [all_names, all_names, col3_names]
        self.plotcontrols.reset_col_boxes(col_names)
        self.update_sel_cols()

    def update_sel_cols(self, new_num=None):
        self.prev_sel_col_names = self.sel_col_names
        self.sel_col_names = self.plotcontrols.get_sel_cols()
        # Try to make 1D plot if '---' is selected in the third comboBox.
        self.plot_is_2D = self.sel_col_names[2] != self.none_str
        self.data_is_1D = self.sweep.dimension == 1
        plot_is_invalid = self.plot_is_2D and self.data_is_1D
        if plot_is_invalid:
            msg = "You can't do an image plot, since the data is only 1D."
            self.statusBar.showMessage(msg, 2000)
            self.plotcontrols.set_text_on_box(2, self.none_str)
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
                try:
                    self.plot_data[i] = self.sweep.pdata[col_name]
                except Exception as error:
                    msg = ('Calculation of pseudocolumn failed. No plot action'
                           ' taken.')
                    self.statusBar.showMessage(msg, 2000)
                    pass
        self.set_data_for_imshow()

    def set_data_for_imshow(self):
        if not self.plot_is_2D:
            return
        col0_axis = arr_varies_monotonically_on_axis(self.plot_data[0])
        col1_axis = arr_varies_monotonically_on_axis(self.plot_data[1])
        if not set((col0_axis, col1_axis)) == set((0, 1)):
            msg = 'Selected columns not valid for image plot. No action taken.'
            self.sel_col_names = self.prev_sel_col_names
            self.statusBar.showMessage(msg, 2000)
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
        For both 1D and 2D plots extent is data limits.
        """
        ext = [None] * 3
        user_lims = self.plotcontrols.get_lims()
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
            cmap_name = self.cmap_names[cmap_name]
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
        try:
            self.cbar.remove()
            self.cbar = None
            self.image = None
        except AttributeError:
            pass
        for ax in self.canvas.figure.get_axes():
            ax.cla()
            ax.plot(self.plot_data[0], self.plot_data[1])
            ax.autoscale_view(True, True, True)
        self.common_plot_update()

    def update_2D_plot(self):
        fig = self.canvas.figure
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
        self.image.set_clim(self.lims[2])
        self.cbar.set_label(self.labels[2])
        self.cbar.draw_all()
        ax.autoscale_view(True, True, True)
        self.common_plot_update()

    def common_plot_update(self):
        self.update_is_scheduled = False
        ax = self.canvas.figure.get_axes()[0]
        ax.relim()
        ax.set_xlabel(self.labels[0])
        ax.set_ylabel(self.labels[1])
        ax.set_xlim(self.lims[0])
        ax.set_ylim(self.lims[1])
        ax.set_title(self.sweep.meta['name'], fontsize=10)
        self.custom_tight_layout()
        self.canvas.draw()

    def custom_tight_layout(self):
        # Sometimes we'll get an error:
        # ValueError: bottom cannot be >= top
        # This is a confirmed bug when using tight_layout():
        # https://github.com/matplotlib/matplotlib/issues/5456
        try:
            self.canvas.figure.tight_layout()
        except ValueError:
            msg = ('Title is wider than figure.'
                   'This causes undesired behavior and is a known bug.')
            self.statusBar.showMessage(msg, 2000)

    def init_fig_and_canvas(self):
        fig = Figure()
        fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasQTAgg(fig)
        policy = QSizePolicy.Expanding
        self.canvas.setSizePolicy(policy, policy)
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.canvas.mpl_connect('button_press_event', self.on_key_press)

    def init_navi_toolbar(self):
        self.navi_toolbar = NavigationToolbar2QT(self.canvas, self)
        self.navi_toolbar.setStyleSheet('border: none')
        self.navi_toolbar.setMaximumHeight(20)

    def on_key_press(self, event):
        self.parent.set_active_layout(self)
        try:
            key_press_handler(event, self.canvas, self.navi_toolbar)
        except:
            pass

    def copy_fig_to_clipboard(self):
        image = QtWidgets.QWidget.grab(self.canvas).toImage()
        QtWidgets.QApplication.clipboard().setImage(image)

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
