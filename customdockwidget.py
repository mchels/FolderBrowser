from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDockWidget


class CustomDockWidget(QDockWidget):
    def __init__(self, *args, **kwargs):
        QDockWidget.__init__(self, *args, **kwargs)
        self.installEventFilter(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def focusInEvent(self, QFocusEvent):
        try:
            color_str = 'background-color: lightblue'
            self.widget().navi_toolbar.setStyleSheet(color_str)
        except:
            pass
        QDockWidget.focusInEvent(self, QFocusEvent)

    def focusOutEvent(self, QFocusEvent):
        try:
            self.widget().navi_toolbar.setStyleSheet('background-color: 10')
        except:
            pass
        QDockWidget.focusOutEvent(self, QFocusEvent)
