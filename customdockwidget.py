from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDockWidget


class CustomDockWidget(QDockWidget):
    def __init__(self, title, parent, *args, **kwargs):
        QDockWidget.__init__(self, title)
        self.parent = parent
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def focusInEvent(self, QFocusEvent):
        self.parent.set_active_layout(self.widget())
        QDockWidget.focusInEvent(self, QFocusEvent)
