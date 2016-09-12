import sys
from matplotlib.backends import qt_compat
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore
from FileListWidget import FileList
from sweep import Sweep
from mpllayout import MplLayout


class FolderBrowser(QtGui.QMainWindow):
    def __init__(self, n_figs, dir_path, name_func_dict, window_title='FolderBrowser'):
        self.dir_path = dir_path
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(window_title)
        self.file_list = FileList(self.dir_path)
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Dad, I'm hungry. Hi Hungry, I'm dad.")
        self.name_func_dict = name_func_dict
        self.mpl_layouts = [None] * n_figs
        for i in range(n_figs):
            self.mpl_layouts[i] = MplLayout(statusBar=self.statusBar)
        self.file_list.itemClicked.connect(self.delegate_new_sweep)
        self.dock_widgets = [None] * (n_figs+1)
        for i, mpl_layout in enumerate(self.mpl_layouts):
            widget_title = 'Plot {}'.format(i)
            dock_widget = QtGui.QDockWidget(widget_title, self)
            dock_widget.setWidget(mpl_layout)
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock_widget)
            dock_widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
            self.dock_widgets[i] = dock_widget
        dock_widget = QtGui.QDockWidget('Browser', self)
        dock_widget.setWidget(self.file_list)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)
        dock_widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        file_list_item = self.file_list.currentItem()
        self.delegate_new_sweep(file_list_item)
        self.setDockNestingEnabled(True)
        ava_space = QtGui.QDesktopWidget().availableGeometry()
        self.move(ava_space.x()+0.5*ava_space.width(), 0)
        self.resize(ava_space.width()*0.49, ava_space.height()*0.96)
        self.show()

    def delegate_new_sweep(self, file_list_item):
        sweep_path = file_list_item.data(QtCore.Qt.UserRole)
        self.sweep = Sweep(sweep_path)
        self.sweep.set_pdata(self.name_func_dict)
        for mpl_layout in self.mpl_layouts:
            mpl_layout.reset_and_plot(self.sweep)


if __name__=='__main__':
    from pcols import name_func_dict
    n_figs = 2
    data_path = 'C:/Dropbox/PhD/sandbox_phd/FolderBrowser/data'
    qApp = QtGui.QApplication(sys.argv)
    brw = FolderBrowser(n_figs, data_path, name_func_dict)
    sys.exit(qApp.exec_())
    #qApp.exec_()
