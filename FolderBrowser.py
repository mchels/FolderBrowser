from __future__ import unicode_literals
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

import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
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
        self.navi_toolbar = NavigationToolbar(self.fig_canvas, self)
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
        # TODO Clear figure at some point here.
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
    def __init__(self, dir_path, window_title='FolderBrowser'):
        self.dir_path = dir_path
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(window_title)

        self.file_list = FileList(self.dir_path)
        # As soon as file list is initialized we can load the sweep it has
        # selected.
        self.mpllayout = MplLayout()
        file_list_item = self.file_list.currentItem()
        self.file_list.itemClicked.connect(self.delegate_new_sweep)
        self.delegate_new_sweep(file_list_item)

        self.dock_widget1 = QtGui.QDockWidget('Plot 1', self)
        self.dock_widget1.setWidget(self.mpllayout)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dock_widget1)
        self.dock_widget3 = QtGui.QDockWidget('Browser', self)
        self.dock_widget3.setWidget(self.file_list)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock_widget3)

        self.setCentralWidget(self.dock_widget1)
        
    def delegate_new_sweep(self, file_list_item):
        sweep_path = file_list_item.data(QtCore.Qt.UserRole)
        self.sweep = Sweep(sweep_path)
        self.mpllayout.reset_and_plot(self.sweep)


data_path = 'C:/Dropbox/PhD/sandbox_phd/load_in_jupyter/data'
qApp = QtGui.QApplication(sys.argv)
aw = FolderBrowser(data_path)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
