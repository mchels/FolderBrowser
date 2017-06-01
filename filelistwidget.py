from PyQt5 import QtCore, QtWidgets
import os
import json

class FileList(QtWidgets.QListWidget):
    """
    Contains a list of sweeps to plot.
    """
    def __init__(self, main_dir_path):
        super().__init__()
        self.main_dir_path = main_dir_path
        self.setSortingEnabled(True)
        self.sortItems(order=QtCore.Qt.DescendingOrder)
        self.reload_items()
        self.setCurrentRow(0)

    def reload_items(self):
        self.clear()
        self.item_dict = {}
        self.load_sweeps_in_dir()
        self.set_items()

    def load_sweeps_in_dir(self):
        dir_walker = os.walk(self.main_dir_path, followlinks=False)
        for sub_dir_path, _, fnames in dir_walker:
            if 'meta.json' in fnames:
                json_path = os.path.join(sub_dir_path, 'meta.json')
                with open(json_path) as json_file:
                    meta = json.load(json_file)
                date_and_serial_num = os.path.split(sub_dir_path)[-1]
                item_text = date_and_serial_num + ' ' + meta['name']
                self.item_dict[item_text] = sub_dir_path

    def set_items(self):
        for item_text, sub_dir_path in self.item_dict.items():
            item = QtWidgets.QListWidgetItem(item_text, parent=self)
            # QtCore.Qt.UserRole is simply the integer 32 and denotes the role
            # of the data. That seems super weird.
            item.setData(QtCore.Qt.UserRole, sub_dir_path)
            self.addItem(item)
