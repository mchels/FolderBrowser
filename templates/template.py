import sys
path_to_folderbrowser_directory = '..'
sys.path.append(path_to_folderbrowser_directory)
from folderbrowser import FolderBrowser
from PyQt5 import QtWidgets
import numpy as np
from pcols import name_func_dict

n_figs = 2
win_t = 'Your title here'
data_path = '../data'
qApp = QtWidgets.QApplication(sys.argv)
brw = FolderBrowser(n_figs, data_path, name_func_dict)
sys.exit(qApp.exec_())
