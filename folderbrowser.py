import sys
import os
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QDesktopWidget, QShortcut
from PyQt5.QtGui import QKeySequence
from filelistwidget import FileList
from sweep import Sweep
from mpllayout import MplLayout
from customdockwidget import CustomDockWidget


class FolderBrowser(QMainWindow):
    def __init__(self, n_layouts, dir_path, name_func_dict,
                 window_title='FolderBrowser'):
        QMainWindow.__init__(self)
        self.n_layouts = n_layouts
        self.dir_path = dir_path
        self.name_func_dict = name_func_dict
        self.setWindowTitle(window_title)
        self.dock_widgets = []
        self.init_statusbar()
        self.init_mpl_layouts()
        self.init_file_list()
        self.setDockNestingEnabled(True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.set_hotkeys()
        self.show()

    def set_new_sweep(self):
        file_list_item = self.file_list.currentItem()
        sweep_path = file_list_item.data(QtCore.Qt.UserRole)
        self.sweep = Sweep(sweep_path)
        self.sweep.set_pdata(self.name_func_dict)
        title = self.compose_title(self.sweep, sweep_path)
        for mpl_layout in self.mpl_layouts:
            mpl_layout.set_title(title)
            mpl_layout.reset_and_plot(self.sweep)

    def init_statusbar(self):
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)

    def init_mpl_layouts(self):
        self.mpl_layouts = [None] * self.n_layouts
        for i in range(self.n_layouts):
            self.mpl_layouts[i] = MplLayout(statusBar=self.statusBar,
                                            parent=self)
        for i, mpl_layout in enumerate(self.mpl_layouts):
            title = 'Plot {}'.format(i)
            dock_widget = CustomDockWidget(title, self)
            dock_widget.setWidget(mpl_layout)
            dock_widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock_widget)
            self.dock_widgets.append(dock_widget)
        self.set_active_layout(self.mpl_layouts[0])

    def init_file_list(self):
        self.file_list = FileList(self.dir_path)
        self.file_list.itemClicked.connect(self.set_new_sweep)
        dock_widget = QDockWidget('Browser', self)
        dock_widget.setWidget(self.file_list)
        dock_widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)
        self.dock_widgets.append(dock_widget)

    def set_active_layout(self, layout):
        try:
            inactive_str = 'background-color: 10; border: none'
            self.active_layout.navi_toolbar.setStyleSheet(inactive_str)
        except AttributeError:
            pass
        active_str = 'background-color: lightblue; border: none'
        layout.navi_toolbar.setStyleSheet(active_str)
        self.active_layout = layout

    def copy_active_fig(self):
        self.active_layout.copy_fig_to_clipboard()
        self.statusBar.showMessage('Active figure copied', 1000)

    def set_hotkeys(self):
        self.copy_fig_hotkey = QShortcut(QKeySequence('Ctrl+C'), self)
        self.copy_fig_hotkey.activated.connect(self.copy_active_fig)

    def showEvent(self, event):
        ava_space = QDesktopWidget().availableGeometry()
        self.move(ava_space.x()+0.5*ava_space.width(), 0)
        self.resize(ava_space.width()*0.49, ava_space.height()*0.96)
        self.set_new_sweep()

    @staticmethod
    def compose_title(sweep, sweep_path):
        sweep_name = sweep.meta['name']
        date_stamp = os.path.basename(sweep_path)
        return date_stamp + '\n' + sweep_name


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
