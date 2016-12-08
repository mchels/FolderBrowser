import sys
import os
path_to_folderbrowser_directory = '..'
sys.path.append(path_to_folderbrowser_directory)
from folderbrowser import FolderBrowser
from PyQt5 import QtWidgets
import numpy as np
import matplotlib.pyplot as plt

cwd = os.getcwd()
n_figs = 2
win_t = 'Your title here'
data_path = os.path.normpath(os.path.join(cwd, '../data'))
pcols_path = os.path.normpath(os.path.join(cwd, 'pcols.py'))
qApp = QtWidgets.QApplication(sys.argv)
brw = FolderBrowser(n_figs, data_path, pcols_path)
sys.exit(qApp.exec_())
