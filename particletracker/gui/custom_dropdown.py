from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class QCustomDropdown(QWidget):
    """
    This is used as one method of displaying options for parameter selection for the 
    different tracking methods. (ie if there is a finite list of choices).  The parameters dictionary specifies
    these as a value and a tuple: e.g 'show_output':[False, ('True','False')].   
    It is not used for the actual adding methods drop down. This is in the custom_combo_box.py 
    """

    returnPressed = pyqtSignal()

    def __init__(self, title=None, value_=None, options=None, *args, **kwargs):
        super(QCustomDropdown, self).__init__(*args,**kwargs)
        self.title=title
        self.value_ = value_
        self.options = options
        self.vbox = QHBoxLayout()
        self.label = QLabel(title)
        self.dropdown = QComboBox()
        self.font = QFont()
        self.font.setPointSize(12)
        self.add_options(title)
        if type(value_) == bool:
            if value_:
                value_='True'
            else:
                value_='False'
        if value_ is None:
            value_ = 'None'
        if type(value_) == int:
            value_ = str(value_)
        elif type(value_) == float:
            value_ = str(value_)
        self.dropdown.setCurrentText(value_)
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.dropdown)
        self.setLayout(self.vbox)

    def add_options(self, title):
        for item in self.options:
            self.dropdown.addItem(item)
        self.dropdown.activated[str].connect(lambda x:self.onValueChanged(x))
    
    def onValueChanged(self, get_value):
        text = self.dropdown.currentText()
        self.value_ = text
        self.returnPressed.emit()
        
        