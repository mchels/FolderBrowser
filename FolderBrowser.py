import sys
import os
from matplotlib.backends import qt_compat
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

from FileListWidget import FileList
sys.path.append('C:/git_repos')
from data_loader.sweep import Sweep

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
import matplotlib.pyplot as plt


class MplLayout(QtGui.QWidget):
    """
    Contains canvas, toolbar and three comboboxes.
    """
    def __init__(self):
        super(MplLayout, self).__init__()
        fig, _ = plt.subplots()
        self.fig_canvas = FigureCanvasQTAgg(fig)
        layout = QtGui.QGridLayout()
        self.sel_col_idx = [0, 1, 2]
        self.sel_col_names = ['', '', '']
        n_rows_canvas = 3
        n_cols_canvas = 3
        self.comboBoxes = [None] * 3
        for i in (0, 1, 2):
            self.comboBoxes[i] = QtGui.QComboBox(self)
            self.comboBoxes[i].activated.connect(self.update_sel_cols)
            layout.addWidget(self.comboBoxes[i], n_rows_canvas+1, i, 1, 1)
        layout.addWidget(self.fig_canvas, 1, 0, n_rows_canvas, n_cols_canvas)
        self.navi_toolbar = NavigationToolbar2QT(self.fig_canvas, self)
        layout.addWidget(self.navi_toolbar, 0, 0, 1, n_cols_canvas)
        self.setLayout(layout)

    def reset_comboboxes(self):
        for i in (0, 1, 2):
            self.comboBoxes[i].clear()
            self.comboBoxes[i].addItems(self.sweep.data.dtype.names)
            self.comboBoxes[i].setCurrentIndex(self.sel_col_idx[i])
        self.update_sel_col_names()

    def update_sel_cols(self, new_num):
        self.update_sel_col_idxs()
        self.update_sel_col_names()
        self.update_plot()

    def update_sel_col_idxs(self):
        for i, comboBox in enumerate(self.comboBoxes):
            self.sel_col_idx[i] = comboBox.currentIndex()

    def update_sel_col_names(self):
        """
        This function does not support pseudocolumns yet. It only searches
        in the raw data columns for the column name corresponding an index.
        """
        for i, idx in enumerate(self.sel_col_idx):
            self.sel_col_names[i] = self.sweep.data.dtype.names[idx]

    def reset_and_plot(self, sweep=None):
        if sweep is not None:
            self.sweep = sweep
        self.reset_comboboxes()
        for i, col in enumerate(self.sel_col_names):
            if not col:
                for new_col in self.sweep.data.dtype.names:
                    if new_col not in self.sel_col_names:
                        self.sel_col_names[i] = new_col
        self.update_plot()

    def update_plot(self):
        x_data = self.sweep.data[self.sel_col_names[0]]
        y_data = self.sweep.data[self.sel_col_names[1]]
        for ax in self.fig_canvas.figure.get_axes():
            ax.cla()
            ax.plot(x_data, y_data)
            ax.relim()
            ax.autoscale_view(True, True, True)
        self.fig_canvas.figure.tight_layout()
        self.fig_canvas.figure.canvas.draw()


class FolderBrowser(QtGui.QMainWindow):
    def __init__(self, n_figs, dir_path, window_title='FolderBrowser'):
        self.dir_path = dir_path
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(window_title)
        self.file_list = FileList(self.dir_path)
        self.mpl_layouts = [None] * n_figs
        for i in range(n_figs):
            self.mpl_layouts[i] = MplLayout()
        self.file_list.itemClicked.connect(self.delegate_new_sweep)
        self.dock_widgets = [None] * (n_figs+1)
        for i, mpl_layout in enumerate(self.mpl_layouts):
            widget_title = 'Plot {}'.format(i)
            dock_widget = QtGui.QDockWidget(widget_title, self)
            dock_widget.setWidget(mpl_layout)
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock_widget)
            self.dock_widgets[i] = dock_widget
        dock_widget = QtGui.QDockWidget('Browser', self)
        dock_widget.setWidget(self.file_list)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)
        self.dock_widgets[-1] = dock_widget
        # Set central widget to the first mpl_layout.
        self.setCentralWidget(self.dock_widgets[0])
        file_list_item = self.file_list.currentItem()
        self.delegate_new_sweep(file_list_item)
        self.show()

    def delegate_new_sweep(self, file_list_item):
        sweep_path = file_list_item.data(QtCore.Qt.UserRole)
        self.sweep = Sweep(sweep_path)
        for mpl_layout in self.mpl_layouts:
            mpl_layout.reset_and_plot(self.sweep)


n_figs = 2
data_path = 'C:/Dropbox/PhD/sandbox_phd/load_in_jupyter/data'
qApp = QtGui.QApplication(sys.argv)
brw = FolderBrowser(n_figs, data_path)
sys.exit(qApp.exec_())
#qApp.exec_()
