import sys
import os
import platform
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QDesktopWidget, QShortcut
from PyQt5.QtGui import QKeySequence
from filelistwidget import FileList
from sweep import Sweep
from mpllayout import MplLayout
from customdockwidget import CustomDockWidget
from textforcopying import TextForCopying
import importlib.util
import textwrap


def show_loading(func):
    def func_wrapper(self, *args, **kwargs):
        self.statusBar.showMessage('Loading...')
        func(self, *args, **kwargs)
        self.statusBar.showMessage('')
    return func_wrapper


class FolderBrowser(QMainWindow):
    """
    This class is the main window.

    Parameters
    ----------
    n_layouts : integer
        Number of desired MplLayouts. Cannot be changed after the window has
        loaded.
    dir_path : string
        Fully qualified path to the directory containing data folders.
    pcols_path : string
        Fully qualified path to the .py file containing functions to calculate
        pseudocolumns.
    window_title : string
        Title of the window.
    """
    def __init__(self, n_layouts, dir_path, pcols_path,
                 window_title='FolderBrowser'):
        super().__init__()
        self.n_layouts = n_layouts
        self.dir_path = dir_path
        self.pcols_path = pcols_path
        self.assert_exists(dir_path)
        self.assert_exists(pcols_path)
        self.set_pcols()
        self.sweep_name = None
        self.sweep = None
        self.setWindowTitle(window_title)
        self.dock_widgets = []
        self.init_statusbar()
        self.init_mpl_layouts()
        self.load_sweeps_in_dir()
        self.init_file_list()
        self.setDockNestingEnabled(True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.set_hotkeys()
        self.set_icon()
        self.show()

    @show_loading
    def set_new_sweep(self, file_list_widget=None):
        file_list_item = self.file_list.currentItem()
        sweep_name = file_list_item.text()
        sweep_path = self.sweep_dict[sweep_name]['path']
        self.sweep = Sweep(sweep_path)
        self.sweep_path = sweep_path
        self.sweep.set_pdata(self.pcols.name_func_dict)
        for mpl_layout in self.mpl_layouts:
            title_wrapped = self.wrap_title(sweep_name, mpl_layout)
            mpl_layout.set_title(title_wrapped)
            mpl_layout.reset_and_plot(self.sweep)
        self.sweep_name = sweep_name

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

    def load_sweeps_in_dir(self):
        self.sweep_dict = {}
        dir_walker = os.walk(self.dir_path, followlinks=False)
        for sub_dir_path, _, fnames in dir_walker:
            try:
                meta = Sweep.load_dir(sub_dir_path, meta_only=True)
            except FileNotFoundError:
                continue
            time_stamp = os.path.split(sub_dir_path)[-1]
            sweep_name = time_stamp + ' ' + meta['name']
            self.sweep_dict[sweep_name] = {}
            self.sweep_dict[sweep_name]['path'] = sub_dir_path
            self.sweep_dict[sweep_name]['time_stamp'] = time_stamp

    def init_file_list(self):
        names = self.sweep_dict.keys()
        self.file_list = FileList(names)
        self.file_list.itemClicked.connect(self.set_new_sweep)
        self.file_list.itemActivated.connect(self.set_new_sweep)
        dock_widget = QDockWidget('Browser', self)
        dock_widget.setWidget(self.file_list)
        dock_widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)
        self.dock_widgets.append(dock_widget)

    def reload_file_list(self):
        self.load_sweeps_in_dir()
        names = self.sweep_dict.keys()
        self.file_list.names = names
        self.file_list.reload_items()
        msg = 'File list reloaded.'
        self.statusBar.showMessage(msg, 1000)

    def set_active_layout(self, layout):
        try:
            inactive_str = 'background-color: 10; border: none'
            self.active_layout.navi_toolbar.setStyleSheet(inactive_str)
        except AttributeError:
            pass
        active_str = 'background-color: lightblue; border: none'
        layout.navi_toolbar.setStyleSheet(active_str)
        self.active_layout = layout

    def set_hotkeys(self):
        self.open_folder_hotkey = QShortcut(QKeySequence('F2'), self)
        self.open_folder_hotkey.activated.connect(self.code_to_clipboard)
        self.open_folder_hotkey = QShortcut(QKeySequence('F5'), self)
        self.open_folder_hotkey.activated.connect(self.reload_file_list)
        self.open_folder_hotkey = QShortcut(QKeySequence('F6'), self)
        self.open_folder_hotkey.activated.connect(self.reload_pcols)
        self.copy_fig_hotkey = QShortcut(QKeySequence('Ctrl+c'), self)
        self.copy_fig_hotkey.activated.connect(self.copy_active_fig)
        self.open_folder_hotkey = QShortcut(QKeySequence('Ctrl+t'), self)
        self.open_folder_hotkey.activated.connect(self.show_text_for_copying)
        self.open_folder_hotkey = QShortcut(QKeySequence('Ctrl+w'), self)
        self.open_folder_hotkey.activated.connect(self.close)
        self.open_folder_hotkey = QShortcut(QKeySequence('Ctrl+Shift+o'), self)
        self.open_folder_hotkey.activated.connect(self.open_folder)

    def copy_active_fig(self):
        self.active_layout.copy_fig_to_clipboard()
        active_dock_widget = self.active_layout.parentWidget()
        title = active_dock_widget.windowTitle()
        msg = 'Figure in ' + title + ' copied to clipboard'
        self.statusBar.showMessage(msg, 1000)

    def open_folder(self):
        if platform.system() != 'Windows':
            err_msg = '"Open folder" hotkey only implemented on Windows'
            self.statusBar.showMessage(err_msg)
            return
        norm_path = os.path.normpath(self.sweep_path)
        cmd = ['explorer', norm_path]
        subprocess.Popen(cmd)

    def show_text_for_copying(self):
        if self.sweep is None:
            msg = 'No sweep selected. Select a sweep to show its information.'
            self.statusBar.showMessage(msg, 3000)
            return
        lay = self.active_layout
        title = self.sweep_name
        time_stamp = self.sweep_dict[self.sweep_name]['time_stamp']
        name = lay.title
        diag = TextForCopying(title, time_stamp, name, *lay.labels)
        diag.setWindowModality(QtCore.Qt.ApplicationModal)
        diag.setModal(True)
        diag.exec_()

    def set_icon(self):
        app_icon = QtGui.QIcon()
        icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
        for size in (16, 24, 32, 48, 256):
            fname = '{}x{}.png'.format(size, size)
            fpath = os.path.join(icons_dir, fname)
            app_icon.addFile(fpath, QtCore.QSize(size,size))
        self.setWindowIcon(app_icon)

    def set_pcols(self):
        spec = importlib.util.spec_from_file_location('', self.pcols_path)
        pcols = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pcols)
        self.pcols = pcols

    def reload_pcols(self):
        self.set_pcols()
        self.sweep.set_pdata(self.pcols.name_func_dict)
        msg = 'pcols reloaded.'
        self.statusBar.showMessage(msg, 1000)

    def code_to_clipboard(self):
        if self.sweep is None:
            msg = 'No sweep selected. Select a sweep to copy its code.'
            self.statusBar.showMessage(msg, 3000)
            return
        own_path = os.path.dirname(os.path.realpath(__file__))
        lay = self.active_layout
        sel_col_names = lay.sel_col_names
        try:
            z_data_code = "sweep.get_data('{}')".format(sel_col_names[2])
        except IndexError:
            z_data_code = None
        foo = {
            'path_to_folderbrowser_dir': self.prep_path_for_template(own_path),
            'pcols_path': self.prep_path_for_template(self.pcols_path),
            'sweep_path': self.prep_path_for_template(self.sweep_path),
            'x_name': self.pad_str(sel_col_names[0]),
            'y_name': self.pad_str(sel_col_names[1]),
            'z_data_code': z_data_code,
            'plot_dim': lay.plot_dim,
            'scilimits': lay.scilimits,
            'xlabel': self.pad_str(lay.labels[0]),
            'ylabel': self.pad_str(lay.labels[1]),
            'xlim': lay.lims[0],
            'ylim': lay.lims[1],
            'aspect': self.pad_str(lay.aspect),
        }
        if lay.plot_is_2D:
            template_name = 'plot_2D.py'
            foo['plot_2D_type'] = self.pad_str(lay.plot_2D_type)
            foo['cmap_name'] = self.pad_str(lay.cmap_name)
            foo['zlim'] = lay.lims[2]
            foo['zlabel'] = self.pad_str(lay.labels[2])
        else:
            template_name = 'plot_1D.py'
        template_path = os.path.join(own_path, 'templates', template_name)
        with open(template_path, 'r') as file:
            tmpl_str = file.read()
        out_str = tmpl_str.format(**foo)
        QtWidgets.QApplication.clipboard().setText(out_str)
        msg = 'Code for figure copied to clipboard.'
        self.statusBar.showMessage(msg, 1000)

    @staticmethod
    def wrap_title(title, mpl_layout):
        """
        The wrapping functionality is not tested against changes in anything,
        e.g., font, font size, screen resolution.
        """
        fig = mpl_layout.canvas.figure
        ax = fig.axes[0]
        ext_pixels = ax.get_window_extent()
        ext_inches = ext_pixels.transformed(fig.dpi_scale_trans.inverted())
        magic_number = 10
        letters_per_line = int(ext_inches.width * magic_number)
        title_wrapped = '\n'.join(textwrap.wrap(title, letters_per_line))
        return title_wrapped

    @classmethod
    def prep_path_for_template(cls, path):
        path_norm = os.path.normpath(path)
        path_norm_fslash = path_norm.replace('\\', '/')
        padded_path_norm_fslash = cls.pad_str(path_norm_fslash)
        return padded_path_norm_fslash

    @staticmethod
    def pad_str(string):
        if isinstance(string, str):
            return "'{}'".format(string)
        return string

    @staticmethod
    def assert_exists(path):
        if not os.path.exists(path):
            raise ValueError('Path {} does not exist'.format(path))
