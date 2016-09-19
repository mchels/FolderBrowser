import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from FileListWidget import FileList
from sweep import Sweep
from mpllayout import MplLayout


class FolderBrowser(QtWidgets.QMainWindow):
    def __init__(self, n_figs, dir_path, name_func_dict, window_title='FolderBrowser'):
        self.dir_path = dir_path
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(window_title)
        self.file_list = FileList(self.dir_path)
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.name_func_dict = name_func_dict
        self.mpl_layouts = [None] * n_figs
        for i in range(n_figs):
            self.mpl_layouts[i] = MplLayout(statusBar=self.statusBar)
        self.file_list.itemClicked.connect(self.delegate_new_sweep)
        self.dock_widgets = [None] * (n_figs+1)
        for i, mpl_layout in enumerate(self.mpl_layouts):
            widget_title = 'Plot {}'.format(i)
            dock_widget = QtWidgets.QDockWidget(widget_title, self)
            dock_widget.setWidget(mpl_layout)
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock_widget)
            dock_widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
            self.dock_widgets[i] = dock_widget
        dock_widget = QtWidgets.QDockWidget('Browser', self)
        dock_widget.setWidget(self.file_list)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)
        dock_widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        file_list_item = self.file_list.currentItem()
        self.delegate_new_sweep(file_list_item)
        self.setDockNestingEnabled(True)
        ava_space = QtWidgets.QDesktopWidget().availableGeometry()
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
    # data_path = 'C:/Dropbox/z_QDev_Morten_Hels/sandbox_phd/FolderBrowser/data'
    # data_path = 'D:/Qdev users/mchels/2016_08_09_cnt_gen5_FI/data/2016_08_09_initial'
    qApp = QtWidgets.QApplication(sys.argv)
    brw = FolderBrowser(n_figs, data_path, name_func_dict)
    sys.exit(qApp.exec_())
    #qApp.exec_()
