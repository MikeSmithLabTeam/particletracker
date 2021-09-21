from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class ComboBoxAndButton(QWidget):
    """
    This widget combines the drop down menu for selecting each 
    method with the push button that results in it being added
    to the draggable list.

    """
    def __init__(self, title, parent, *args, **kwargs):
        self.font = QFont()
        self.font.setPointSize(12)
        super(ComboBoxAndButton, self).__init__(*args, **kwargs)
        self.title=title
        self.parent = parent
        self.param_dict = parent.param_dict
        self.combo_button_layout = QVBoxLayout()
        # Combobox holds names of blueprints for parameters
        self.construct_method_combo_box(title)
        self.add_method_push_button()
        self.setLayout(self.combo_button_layout)

    def construct_method_combo_box(self, title):
        self.combo_box = QComboBox()
        self.combo_box.setFont(self.font)
        for key in list(self.param_dict[title].keys()):
            if key != title + '_method':
                self.combo_box.addItem(key)
        self.combo_button_layout.addWidget(self.combo_box)

    def add_method_push_button(self):
        add_method_button = QPushButton('Add Method')
        add_method_button.setFont(self.font)
        add_method_button.pressed.connect(
                self.add_method_button_click)
        self.combo_button_layout.addWidget(add_method_button)

    def add_method_button_click(self):
        tab_index = self.parent.tabBar().currentIndex()
        dynamic = self.parent.list_draggable_lists[tab_index].dynamic
        title = self.parent.tabBar().tabText(tab_index)
        method = self.combo_box.currentText()
        draggable_list = self.parent.list_draggable_lists[tab_index]
        count = 1

        if dynamic:
            while method in draggable_list.method_list:
                method = method.split('*')[0] + '*' + str(count)
                count = count + 1
            draggable_list.add_item(method, update=True)
        else:
            draggable_list.takeItem(0)
            draggable_list.add_item(method)
            draggable_list.send_signal()

            
            