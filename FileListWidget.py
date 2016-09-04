from PyQt4 import QtGui, QtCore
import os
import json

class FileList(QtGui.QListWidget):
    def __init__(self, dir_path):
        super(FileList, self).__init__()
        self.dir_path = dir_path
        self.name_timestamp_dict = {}
        self.load_sweeps_in_dir()
        for name, dir_path in self.name_timestamp_dict.items():
            item = QtGui.QListWidgetItem(name, parent=self)
            # QtCore.Qt.UserRole is simply the integer 32 and denotes the role 
            # of the data. That seems super weird.
            item.setData(QtCore.Qt.UserRole, dir_path)
            self.addItem(item)
        self.setCurrentRow(0)

    def load_sweeps_in_dir(self):
        for dirpath, dirnames, fnames in os.walk(self.dir_path, followlinks=False):
            if 'meta.json' in fnames:
                json_path = os.path.join(dirpath, 'meta.json')
                with open(json_path) as json_file:
                    meta = json.load(json_file)
                self.name_timestamp_dict[meta['name']] = dirpath
