from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from plotcontrols import PlotControls
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from numpy import nanmin, nanmax
from custom_colormap import get_colormap
from datahandler import data_handler_factory
from plothandler import plot_handler_factory


class MplLayout(QtWidgets.QWidget):
    """
    This class is responsible for drawing the plots.

    Parameters
    ----------
    statusBar : QtWidgets.QStatusBar instance
        statusBar of the parent FolderBrowser instance.
    parent : QtWidgets.QMainWindow instance
        The parent FolderBrowser instance.
    """
    def __init__(self, statusBar=None, parent=None):
        super().__init__()
        self.statusBar = statusBar
        self.parent = parent
        self.init_fig_and_canvas()
        self.cmap_names = ['Reds', 'Blues_r', 'dark symmetric',
                           'light symmetric', 'inferno', 'viridis', 'afmhot']
        self.plot_2D_types = ('Auto', 'imshow', 'pcolormesh')
        self.plotcontrols = PlotControls(self.update_sel_cols,
                                         self.update_cmap,
                                         self.update_lims,
                                         self.cmap_names,
                                         self.set_plot_2D_type,
                                         self.plot_2D_types,
                                         self.update_aspect)
        self.init_navi_toolbar()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.navi_toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.plotcontrols)
        self.setLayout(layout)
        self.none_str = '---'
        self.sel_col_names = self.plotcontrols.get_sel_cols()
        self.plot_data = [None] * 3
        self.cbar = None
        self.cmap_name = self.cmap_names[0]
        self.cmap = plt.get_cmap(self.cmap_name)
        self.lims = [None] * 3
        self.aspect = 'auto'
        self.update_is_scheduled = False
        self.title = None
        self.labels = [None] * 3
        self.scilimits = (-3,3)
        self.n_active_cols = None
        self.plot_2D_type = None

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
        col_names = self.plotcontrols.get_sel_cols()
        new_col_names = [n for n in col_names if n != self.none_str]
        # Try to make 1D plot if '---' is selected in the third comboBox.
        self.plot_is_2D = len(new_col_names) == 3
        self.data_is_1D = self.sweep.dimension == 1
        plot_is_invalid = self.plot_is_2D and self.data_is_1D
        if plot_is_invalid:
            msg = "You can't do a 2D plot, since the data is only 1D."
            self.statusBar.showMessage(msg, 2000)
            self.plotcontrols.set_text_on_box(2, self.none_str)
            return
        self.set_data_for_plot(new_col_names)
        tmp = (self.plot_dim, self.data_h.n_data_arrs)
        if tmp in ((1,2), (2,3)) and self.data_h.data_is_valid:
            self.update_is_scheduled = True
            self.set_labels()
            self.update_lims()
            self.update_plot()
        else:
            self.clear_axis(redraw=True)

    def set_data_for_plot(self, new_col_names):
        new_plot_data = [None] * len(new_col_names)
        for i, col_name in enumerate(new_col_names):
            sweep = self.sweep
            raw_data_col_names = sweep.data.dtype.names
            pdata_col_names = sweep.pdata.name_func_dict.keys()
            if col_name in raw_data_col_names:
                new_plot_data[i] = sweep.data[col_name]
            elif col_name in pdata_col_names:
                try:
                    new_plot_data[i] = sweep.pdata[col_name]
                except Exception as error:
                    msg = 'Calculation of pseudocolumn failed'
                    self.statusBar.showMessage(msg, 2000)
        new_data_h = data_handler_factory(*new_plot_data)
        self.sel_col_names = new_col_names
        self.n_active_cols = len(new_col_names)
        ax = self.canvas.figure.get_axes()[0]
        plot_dim = self.n_active_cols - 1
        self.plot_dim = plot_dim
        self.plot_h = plot_handler_factory(ax, new_data_h, plot_dim=plot_dim)
        self.data_h = new_data_h

    def set_labels(self):
        self.labels = [None] * self.n_active_cols
        for i, _ in enumerate(self.labels):
            col_name = self.sel_col_names[i]
            self.labels[i] = self.sweep.get_label(col_name)

    def update_lims(self):
        """
        user_lims are limits set by user in the lim_boxes.
        For both 1D and 2D plots extent is data limits.
        """
        ext = [None] * self.n_active_cols
        user_lims = self.plotcontrols.get_lims()
        self.lims = [None] * self.n_active_cols
        for i, lim in enumerate(self.lims):
            ext = self.data_h.get_extent_of_data_dim(i)
            self.lims[i] = self.combine_lim_lists(user_lims[i], ext)
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
        self.cmap = get_colormap(cmap_name, self.lims[2])
        if not self.update_is_scheduled:
            self.update_plot()

    def update_aspect(self):
        self.aspect = self.plotcontrols.get_aspect()
        if not self.update_is_scheduled:
            self.update_plot()

    def update_plot(self):
        if self.plot_is_2D: self._update_2D_plot()
        else: self._update_1D_plot()
        self.update_is_scheduled = False

    def _update_1D_plot(self):
        self.clear_axis(redraw=False)
        self.plot_h.plot()
        self.common_plot_update()

    def _update_2D_plot(self):
        fig = self.canvas.figure
        if self.plot_2D_type == 'imshow' and not self.data_h.imshow_eligible:
            self.clear_axis(redraw=True)
            return
        self.clear_axis(redraw=False)
        self.image = self.plot_h.plot(plot_type=self.plot_2D_type)
        self.cbar = fig.colorbar(mappable=self.image)
        self.cbar.formatter.set_powerlimits(self.scilimits)
        self.image.set_cmap(self.cmap)
        self.image.set_clim(self.lims[2])
        self.cbar.set_label(self.labels[2])
        self.cbar.draw_all()
        self.common_plot_update()

    def common_plot_update(self):
        ax = self.canvas.figure.get_axes()[0]
        ax.ticklabel_format(style='sci', axis='both',
                            scilimits=self.scilimits, useOffset=False)
        ax.autoscale_view(True, True, True)
        ax.relim()
        ax.set_xlabel(self.labels[0])
        ax.set_ylabel(self.labels[1])
        ax.set_xlim(self.lims[0])
        ax.set_ylim(self.lims[1])
        ax.set_title(self.title, fontsize=11)
        ax.set_aspect(self.aspect)
        self.custom_tight_layout()
        self.canvas.draw()

    def clear_axis(self, redraw=True):
        try:
            self.cbar.remove()
            self.cbar = None
            self.image = None
        except AttributeError:
            pass
        for ax in self.canvas.figure.get_axes():
            ax.cla()
            ax.relim()
            ax.autoscale()
        if redraw:
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
        fig = Figure(facecolor='white')
        fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasQTAgg(fig)
        policy = QSizePolicy.Expanding
        self.canvas.setSizePolicy(policy, policy)

    def init_navi_toolbar(self):
        self.navi_toolbar = NavigationToolbar2QT(self.canvas, self)
        self.navi_toolbar.setStyleSheet('border: none')
        self.navi_toolbar.setMaximumHeight(20)

    def copy_fig_to_clipboard(self):
        image = QtWidgets.QWidget.grab(self.canvas).toImage()
        QtWidgets.QApplication.clipboard().setImage(image)

    def set_plot_2D_type(self, new_type=None):
        new_type = self.plotcontrols.get_sel_2D_type()
        assert new_type in self.plot_2D_types
        if new_type == 'Auto':
            new_type = None
        self.plot_2D_type = new_type
        if not self.update_is_scheduled:
            self.update_plot()

    def set_title(self, title):
        self.title = title

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
