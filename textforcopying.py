from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QLineEdit, QShortcut, QFormLayout, QLabel
from PyQt5.QtGui import QKeySequence

class TextForCopying(QDialog):
    def __init__(self, title, date_stamp, name, xlabel, ylabel, zlabel):
        super(TextForCopying, self).__init__()
        self.title = title
        self.date_stamp = date_stamp
        self.name = name
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.zlabel = zlabel
        self.labels = ['title', 'date_stamp', 'name', 'xlabel', 'ylabel',
                       'zlabel']
        self.init_geometry()
        self.set_hotkeys()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def init_geometry(self):
        layout = QFormLayout()
        for label in self.labels:
            text = getattr(self, label)
            label = QLabel(label)
            wdg = QLineEdit(text)
            wdg.setMinimumWidth(1000)
            layout.addRow(label, wdg)
        self.setLayout(layout)

    def set_hotkeys(self):
        self.hotkey1 = QShortcut(QKeySequence('Ctrl+w'), self)
        self.hotkey1.activated.connect(self.close)

if __name__=='__main__':
    import sys
    qApp = QtWidgets.QApplication(sys.argv)
    diag = TextForCopying('foo', 'longstriiiiiing', 'foo', 'abc', 'foo', 'foo')
    diag.show()
    sys.exit(qApp.exec_())
