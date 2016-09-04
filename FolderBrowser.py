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


class FolderBrowser(QtGui.QMainWindow):
    def __init__(self, fig, dir_path, window_title='FolderBrowser'):
        self.fig = fig
        self.axes = fig.get_axes()
        self.dir_path = dir_path
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(window_title)

        sub_layout = QtGui.QGridLayout()

        n_rows_canvas = 3
        n_cols_canvas = 3
        canvas = MyNewMplCanvas(fig)
        MPL_widget = QtGui.QWidget()
        sub_layout.addWidget(canvas, 1, 0, n_rows_canvas, n_cols_canvas)

        self.file_list = FileList(self.dir_path)
        self.file_list.itemClicked.connect(canvas.load_and_plot_data)
        canvas.load_and_plot_data(self.file_list.currentItem())

        comboBoxes = [None] * 3
        for i in (0, 1, 2):
            comboBoxes[i] = QtGui.QComboBox(self)
            comboBoxes[i].addItems(canvas.col_names)
            comboBoxes[i].setCurrentIndex(i)
            if i==0:
                comboBoxes[i].currentIndexChanged.connect(canvas.change_sel_col_num0)
            elif i==1:
                comboBoxes[i].currentIndexChanged.connect(canvas.change_sel_col_num1)
            elif i==2:
                comboBoxes[i].currentIndexChanged.connect(canvas.change_sel_col_num1)
            sub_layout.addWidget(comboBoxes[i], n_rows_canvas+1, i, 1, 1)

        self.navi_toolbar = NavigationToolbar(canvas, self)
        sub_layout.addWidget(self.navi_toolbar, 0, 0, 1, n_cols_canvas)

        MPL_widget.setLayout(sub_layout)
        self.dock_widget1 = QtGui.QDockWidget('Plot 1', self)
        self.dock_widget1.setWidget(MPL_widget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dock_widget1)
        self.dock_widget3 = QtGui.QDockWidget('Browser', self)
        self.dock_widget3.setWidget(self.file_list)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock_widget3)

        self.setCentralWidget(self.dock_widget1)


qApp = QtGui.QApplication(sys.argv)

data_path = 'C:/Dropbox/PhD/sandbox_phd/load_in_jupyter/data'
fig, _ = plt.subplots()
aw = FolderBrowser(fig, data_path)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
