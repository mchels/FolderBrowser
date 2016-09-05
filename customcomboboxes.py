from matplotlib.backends import qt_compat
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore


class CustomComboBoxes(object):
    def __init__(self, num_boxes, connect_fct):
        if num_boxes not in (1,2,3):
            raise RuntimeError('Only 1, 2, and 3 boxes are supported.')
        self.num_boxes = num_boxes
        self.boxes = [None] * num_boxes
        for i in range(num_boxes):
            self.boxes[i] = QtGui.QComboBox()
            self.boxes[i].activated.connect(connect_fct)

    def reset(self, array_of_text_items):
        assert len(array_of_text_items) == self.num_boxes
        for i, box in enumerate(self.boxes):
            box.list_of_text_items = array_of_text_items[i]
            prev_text = box.currentText()
            box.clear()
            box.addItems(array_of_text_items[i])
            idx = box.findText(prev_text)
            box.setCurrentIndex(idx)
        # All indices must be set in the loop above before we can start
        # assigning lowest unoccupied texts. Otherwise we don't know which
        # texts are unoccupied.
        for box in self.boxes:
            if box.currentIndex() == -1:
                self.select_lowest_unoccupied(box)

    def get_sel_texts(self):
        sel_texts = [box.currentText() for box in self.boxes]
        return sel_texts

    def select_lowest_unoccupied(self, box):
        """
        Sets the text on box to the lowest text in self.list_of_text_items 
        which is not already occupied by another box.
        """
        sel_texts = self.get_sel_texts()
        for i, text in enumerate(box.list_of_text_items):
            if text not in sel_texts:
                box.setCurrentIndex(i)
                return
