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
from customcomboboxes import CustomComboBoxes

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
import matplotlib.pyplot as plt


class MplLayout(QtGui.QWidget):
    """
    Contains canvas, toolbar and a customcomboboxes object.
    """
    def __init__(self):
        super(MplLayout, self).__init__()
        fig, _ = plt.subplots()
        self.fig_canvas = FigureCanvasQTAgg(fig)
        self.comboBoxes = CustomComboBoxes(3, self.update_sel_cols)
        self.navi_toolbar = NavigationToolbar2QT(self.fig_canvas, self)
        layout = QtGui.QGridLayout()
        n_rows_canvas = 3
        n_cols_canvas = 3
        for i, box in enumerate(self.comboBoxes.boxes):
            layout.addWidget(box, n_rows_canvas+1, i, 1, 1)
        layout.addWidget(self.fig_canvas, 1, 0, n_rows_canvas, n_cols_canvas)
        layout.addWidget(self.navi_toolbar, 0, 0, 1, n_cols_canvas)
        self.setLayout(layout)
        self.none_str = '---'

    def update_sel_cols(self, new_num=None):
        """
        To maintain a consistent state we must update the plot at the end.
        """
        self.sel_col_names = self.comboBoxes.get_sel_texts()
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
