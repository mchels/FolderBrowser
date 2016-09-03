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
    def __init__(self, fig, parent=None):
        self.fig = fig
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.axes = fig.get_axes()

        self.load_and_plot_data()

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def load_and_plot_data(self, file_list_item=None):
        if file_list_item is None:
            # raise RuntimeError('file_list_item is None')
            return
        sweep_path = file_list_item.data(QtCore.Qt.UserRole)
        self.sweep = Sweep(sweep_path)
        sweep_names = self.sweep.data.dtype.names
        x_data = self.sweep.data[sweep_names[0]]
        y_data = self.sweep.data[sweep_names[1]]
        for ax in self.axes:
            ax.cla()
            ax.plot(x_data, y_data)
            ax.relim()
            ax.autoscale_view(True, True, True)
        self.fig.canvas.draw()


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

        comboBox1 = QtGui.QComboBox(self)
        comboBox1.addItems(['wejoif','wjeofij'])
        grid.addWidget(comboBox1, n_rows_canvas, 0, 1, 1)

        comboBox2 = QtGui.QComboBox(self)
        comboBox2.addItems(['xvmnb','xvbzxcnm'])
        grid.addWidget(comboBox2, n_rows_canvas, 1, 1, 2)

        self.navi_toolbar = NavigationToolbar(canvas, self)
        grid.addWidget(self.navi_toolbar, n_rows_canvas+1, 0, 1, n_cols_canvas)

        self.file_list = FileList(self.dir_path)
        self.file_list.itemClicked.connect(canvas.load_and_plot_data)
        grid.addWidget(self.file_list, n_rows_canvas+2, 0, 2, n_cols_canvas)
        canvas.load_and_plot_data(self.file_list.currentItem())


qApp = QtGui.QApplication(sys.argv)

data_path = 'C:/Dropbox/PhD/sandbox_phd/load_in_jupyter/data'
fig, _ = plt.subplots()
aw = FolderBrowser(fig, data_path)
aw.setWindowTitle('Some cool title for the window')
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
