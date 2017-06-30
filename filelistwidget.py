from PyQt5 import QtCore, QtWidgets
from sweep import Sweep
import os

class FileList(QtWidgets.QListWidget):
    """
    Contains a list of sweeps to plot.
    """
    def __init__(self, names):
        super().__init__()
        self.names = names
        self.setSortingEnabled(True)
        self.sortItems(order=QtCore.Qt.DescendingOrder)
        self.reload_items()
        self.setCurrentRow(0)

    def reload_items(self):
        self.clear()
        self.set_items()

    def set_items(self):
        for name in self.names:
            item = QtWidgets.QListWidgetItem(name, parent=self)
            self.addItem(item)
