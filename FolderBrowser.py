from __future__ import unicode_literals
import sys
import os
from matplotlib.backends import qt_compat
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

#fjoweifjwe
from FileListWidget import FileList
sys.path.append('C:/git_repos')
from data_loader.sweep import Sweep

import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class MyNewMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, fig):
        self.fig = fig
        FigureCanvas.__init__(self, fig)
        self.axes = fig.get_axes()
        self.sel_col_names = ['', '', '']

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    # Distinguish between updating the plot and changing the sweep and redrawing it completely!
    def load_and_plot_data(self, file_list_item=None):
        # if file_list_item is None:
            # raise RuntimeError('file_list_item is None')
            # return
        if file_list_item is not None:
            sweep_path = file_list_item.data(QtCore.Qt.UserRole)
            self.sweep = Sweep(sweep_path)
        if self.sweep.dimension != 1:
            err_str = 'Dimension {} not yet supported'.format(sweep.dimension)
            raise RuntimeError(err_str)
        self.col_names = self.sweep.data.dtype.names
        for i, col in enumerate(self.sel_col_names):
            if not col:
                for new_col in self.col_names:
                    if new_col not in self.sel_col_names:
                        self.sel_col_names[i] = new_col
        x_data = self.sweep.data[self.sel_col_names[0]]
        y_data = self.sweep.data[self.sel_col_names[1]]
        for ax in self.axes:
            ax.cla()
            ax.plot(x_data, y_data)
            ax.relim()
            ax.autoscale_view(True, True, True)
        fig.tight_layout()
        self.fig.canvas.draw()
        
    def change_sel_col_num0(self, new_num):
        self.sel_col_names[0] = self.col_names[new_num]
        self.load_and_plot_data()

    def change_sel_col_num1(self, new_num):
        self.sel_col_names[1] = self.col_names[new_num]
        self.load_and_plot_data()


class FolderBrowser(QtGui.QWidget):
    def __init__(self, fig, dir_path):
        self.fig = fig
        self.axes = fig.get_axes()
        self.dir_path = dir_path
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)

        n_rows_canvas = 3
        n_cols_canvas = 3
        canvas = MyNewMplCanvas(fig)
        grid.addWidget(canvas, 0, 0, n_rows_canvas, n_cols_canvas)

        self.navi_toolbar = NavigationToolbar(canvas, self)
        grid.addWidget(self.navi_toolbar, n_rows_canvas+1, 0, 1, n_cols_canvas)

        self.file_list = FileList(self.dir_path)
        self.file_list.itemClicked.connect(canvas.load_and_plot_data)
        grid.addWidget(self.file_list, n_rows_canvas+2, 0, 2, n_cols_canvas)
        canvas.load_and_plot_data(self.file_list.currentItem())

        comboBox0 = QtGui.QComboBox(self)
        comboBox0.addItems(canvas.col_names)
        comboBox0.setCurrentIndex(0)
        comboBox0.currentIndexChanged.connect(canvas.change_sel_col_num0)
        grid.addWidget(comboBox0, n_rows_canvas, 0, 1, 1)
        
        
        comboBox1 = QtGui.QComboBox(self)
        comboBox1.addItems(canvas.col_names)
        comboBox1.setCurrentIndex(1)
        comboBox1.currentIndexChanged.connect(canvas.change_sel_col_num1)
        grid.addWidget(comboBox1, n_rows_canvas, 1, 1, 2)


qApp = QtGui.QApplication(sys.argv)

data_path = 'C:/Dropbox/PhD/sandbox_phd/load_in_jupyter/data'
fig, _ = plt.subplots()
aw = FolderBrowser(fig, data_path)
aw.setWindowTitle('Some cool title for the window')
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
