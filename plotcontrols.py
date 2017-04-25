from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy

class PlotControls(QtWidgets.QWidget):
    def __init__(self, sel_col_func, cmap_func, lim_func, cmap_names,
                 plot_2D_type_func, plot_2D_types, aspect_func):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout()
        self.num_col_boxes = 3
        self.num_lim_boxes = 3
        self.sel_col_func = sel_col_func
        self.cmap_func = cmap_func
        self.lim_func = lim_func
        self.cmap_names = cmap_names
        self.plot_2D_type_func = plot_2D_type_func
        self.plot_2D_types = plot_2D_types
        self.aspect_func = aspect_func
        self.init_col_sel_boxes()
        self.init_cmap_sel()
        self.init_plot_2D_type_sel()
        self.init_lim_boxes()
        self.init_aspect_box()
        self.setLayout(self.layout)

    def reset_col_boxes(self, array_of_text_items):
        assert len(array_of_text_items) == self.num_col_boxes
        for i, box in enumerate(self.col_boxes):
            box.list_of_text_items = array_of_text_items[i]
            prev_text = box.currentText()
            box.clear()
            box.addItems(array_of_text_items[i])
            idx = box.findText(prev_text)
            box.setCurrentIndex(idx)
            min_width = len(max(box.list_of_text_items, key=len)) * 8
            box.view().setMinimumWidth(min_width)
        # All indices must be set in the loop above before we can start
        # assigning lowest unoccupied texts. Otherwise we don't know which
        # texts are unoccupied.
        for box in self.col_boxes:
            if box.currentIndex() == -1:
                self.select_lowest_unoccupied(box)

    def init_col_sel_boxes(self):
        self.col_boxes = [None] * self.num_col_boxes
        for i in range(self.num_col_boxes):
            box = QtWidgets.QComboBox()
            box.activated.connect(self.sel_col_func)
            box.setMaxVisibleItems(80)
            policy_horiz = QSizePolicy.MinimumExpanding
            policy_vert = QSizePolicy.Maximum
            box.setSizePolicy(policy_horiz, policy_vert)
            box.setMinimumWidth(40)
            self.layout.addWidget(box)
            self.col_boxes[i] = box

    def init_cmap_sel(self):
        cmap_sel = QtWidgets.QComboBox()
        cmap_sel.addItems(self.cmap_names)
        cmap_sel.activated.connect(self.cmap_func)
        policy_horiz = QSizePolicy.MinimumExpanding
        policy_vert = QSizePolicy.Maximum
        cmap_sel.setSizePolicy(policy_horiz, policy_vert)
        cmap_sel.setMinimumWidth(40)
        min_width = len(max(self.cmap_names, key=len)) * 8
        cmap_sel.view().setMinimumWidth(min_width)
        self.layout.addWidget(cmap_sel)
        self.cmap_sel = cmap_sel

    def init_plot_2D_type_sel(self):
        plot_2D_type_sel = QtWidgets.QComboBox()
        plot_2D_type_sel.addItems(self.plot_2D_types)
        plot_2D_type_sel.activated.connect(self.plot_2D_type_func)
        policy_horiz = QSizePolicy.MinimumExpanding
        policy_vert = QSizePolicy.Maximum
        plot_2D_type_sel.setSizePolicy(policy_horiz, policy_vert)
        plot_2D_type_sel.setMinimumWidth(40)
        min_width = len(max(self.plot_2D_types, key=len)) * 8
        plot_2D_type_sel.view().setMinimumWidth(min_width)
        self.layout.addWidget(plot_2D_type_sel)
        self.plot_2D_type_sel = plot_2D_type_sel

    def init_lim_boxes(self):
        self.lim_boxes = [None] * self.num_lim_boxes
        dim_names = ['x', 'y', 'z']
        for i in range(self.num_lim_boxes):
            lim_box = QtWidgets.QLineEdit()
            lim_box.editingFinished.connect(self.lim_func)
            tooltip = ('Limit for {}. Use <number>:<number> where both numbers '
                       'can be empty').format(dim_names[i])
            lim_box.setToolTip(tooltip)
            self.layout.addWidget(lim_box)
            self.lim_boxes[i] = lim_box

    def init_aspect_box(self):
        aspect_box = QtWidgets.QLineEdit()
        aspect_box.editingFinished.connect(self.aspect_func)
        aspect_box.setToolTip('Aspect ratio, use <number> or <number:number>')
        self.layout.addWidget(aspect_box)
        self.aspect_box = aspect_box

    def get_sel_cols(self):
        sel_texts = [box.currentText() for box in self.col_boxes]
        return sel_texts

    def get_sel_2D_type(self):
        sel_str = self.plot_2D_type_sel.currentText()
        return sel_str

    def get_lims(self):
        lims = [None] * self.num_lim_boxes
        for i, lim_box in enumerate(self.lim_boxes):
            lims[i] = self.parse_lims(lim_box.text())
        return lims

    def get_aspect(self):
        text = self.aspect_box.text()
        return self.parse_aspect(text)

    def select_lowest_unoccupied(self, box):
        """
        Sets the text on box to the text with the lowest index in
        box.list_of_text_items which is not already selected in another box in
        self.col_boxes.
        """
        sel_texts = self.get_sel_cols()
        for i, text in enumerate(box.list_of_text_items):
            if text not in sel_texts:
                box.setCurrentIndex(i)
                return

    def set_text_on_box(self, box_idx, text):
        """
        Potential infinite loop if sel_col_func calls this function.
        """
        box = self.col_boxes[box_idx]
        idx = box.findText(text)
        box.setCurrentIndex(idx)
        self.sel_col_func()

    def parse_lims(self, text):
        lims = text.split(':')
        if len(lims) != 2:
            return (None, None)
        lower_lim = self.conv_to_float_or_None(lims[0])
        upper_lim = self.conv_to_float_or_None(lims[1])
        return (lower_lim, upper_lim)

    def parse_aspect(self, text):
        try: return float(text)
        except ValueError: pass
        parts = text.split(':')
        try:
            num = float(parts[0])
            den = float(parts[1])
        except (ValueError, IndexError):
            return 'auto'
        return num / den

    @staticmethod
    def conv_to_float_or_None(str):
        try:
            return float(str)
        except ValueError:
            return None
