from PyQt5 import QtCore, QtWidgets
import os
import json

class FileList(QtWidgets.QListWidget):
    def __init__(self, main_dir_path):
        super(FileList, self).__init__()
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
                self.item_dict[meta['name']] = sub_dir_path

    def set_items(self):
        for name, sub_dir_path in self.item_dict.items():
            date_and_serial_num = os.path.split(sub_dir_path)[-1]
            item_name = date_and_serial_num + ' ' + name
            item = QtWidgets.QListWidgetItem(item_name, parent=self)
            # QtCore.Qt.UserRole is simply the integer 32 and denotes the role
            # of the data. That seems super weird.
            item.setData(QtCore.Qt.UserRole, sub_dir_path)
            self.addItem(item)
