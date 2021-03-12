from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qtwidgets import QCustomSlider, QCustomTextBox, SelectAreaWidget
from .custom_textbox import QModCustomTextBox
from .custom_dropdown import QCustomDropdown

class CollectionParamAdjustors(QWidget):
    def __init__(self, title, param_dict, param_change, *args, **kwargs):
        super(CollectionParamAdjustors, self).__init__(*args, **kwargs)
        self.title = title
        self.param_change = param_change
        self.scroll_layout = QVBoxLayout()
        self.build_widgets(title, param_dict)

        
    def build_widgets(self, title, param_dict):
        self.layout_outer = QVBoxLayout()
        for method in param_dict[title + '_method']:
            widget_count=0
            group_box = QGroupBox(method)
            vbox = QVBoxLayout()

            """
            Read the datatype of param dictionary. Use this to determine
            what type of gui object (slider, text box etc) to display for adjustment.
            """
            if isinstance(param_dict[method], dict):
                for method_param in list(param_dict[method].keys()):
                    # If sub dictionary contains a list [value, min, max, step] gui displays a QCustomSlider
                    if isinstance(param_dict[method][method_param], list):
                        if len(param_dict[method][method_param]) == 4:
                            slider = QCustomSlider(title = method_param,
                                                min_ = param_dict[method][method_param][1],
                                                max_ = param_dict[method][method_param][2],
                                                step_ = param_dict[method][method_param][3],
                                                value_ = param_dict[method][method_param][0],
                                                spinbox = True,
                                                )
                            #Add location within dictionary as metadata
                            slider.meta = [title, method, method_param]
                            slider.widget = 'slider'
                            #Signal connected to param_change slot. This is in toplevel.py
                            slider.valueChanged.connect(lambda x=None: self.param_change(x))
                            vbox.addWidget(slider)
                            widget_count += 1
                        else:
                            dropdown=QCustomDropdown(title=method_param, value_=param_dict[method][method_param][0],options=param_dict[method][method_param][1])
                            dropdown.meta = [title, method, method_param]
                            dropdown.widget = 'dropdown'
                            dropdown.returnPressed.connect(lambda x=None: self.param_change(x))
                            vbox.addWidget(dropdown)
                            widget_count += 1
                    #if some other datatype display edit text boxes
                    else:
                        textbox = QCustomTextBox(title=method_param, value_=param_dict[method][method_param])
                        # Add location within dictionary as metadata
                        textbox.meta = [title, method, method_param]
                        textbox.widget = 'textbox'
                        # Signal connected to param_change slot. This is in toplevel.py
                        textbox.returnPressed.connect(lambda x=textbox.text: self.param_change(x))
                        vbox.addWidget(textbox)#Text_Box(method_param,method, param_dict, param_change))
                        widget_count += 1

            # Edit Text boxes as top level entries
            elif isinstance(param_dict[method], str) \
                    or isinstance(param_dict[method], int) \
                    or isinstance(param_dict[method], float)\
                    or isinstance(param_dict[method], tuple)\
                    or isinstance(param_dict[method], type(None)):
                textbox = QCustomTextBox(title=method, value_=param_dict[method])
                # Add location within dictionary as metadata
                textbox.meta = [title, method]
                textbox.widget = 'textbox'
                # Signal connected to param_change slot. This is in toplevel.py
                textbox.returnPressed.connect(lambda x=None: self.param_change(x))
                vbox.addWidget(textbox)
                widget_count += 1

            if widget_count > 0:
                group_box.setLayout(vbox)
                self.layout_outer.addWidget(group_box)
            else:
                group_box.deleteLater()     
        self.widget_container = QWidget()
        self.widget_container.setLayout(self.layout_outer)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.widget_container)
        
        self.scroll_layout.addWidget(scroll)
        self.setLayout(self.scroll_layout)  ,

    def remove_widgets(self):     
        num_widgets = self.scroll_layout.count()
        for i in reversed(range(num_widgets)):
            item = self.scroll_layout.itemAt(i)
            item.widget().setParent(None)
            

class CropMask(QWidget):
    valueChanged = pyqtSignal(str)

    def __init__(self, title, param_dict, param_change, img_viewer, parent=None, *args, **kwargs):
        super(CropMask, self).__init__(*args, **kwargs)
        if parent is not None:
            self.parent=parent
        self.img_viewer=img_viewer
        self.title = title
        self.param_change=param_change
        self.param_dict = param_dict
        self.layout = QHBoxLayout()
        self.build_widgets(title, param_dict)

    def build_widgets(self, title, param_dict):   
        self.layout_outer = QVBoxLayout()     
        self.edit_widget_list = []
        self.active_methods = list(self.param_dict['crop_method'])

        for method in param_dict[title + '_method']:
            textbox = QModCustomTextBox(self.img_viewer, parent=self.parent, title=method, value_=str(self.param_dict[method]), checkbox=True)
            textbox.meta = [title, method]
            textbox.widget='textbox'
            textbox.returnPressed.connect(lambda x=textbox.value(): self.param_change(x))
            self.layout_outer.addWidget(textbox)
        reset_button=QPushButton('Reset')
        reset_button.meta = 'ResetMask'
        reset_button.clicked.connect(lambda x='DummyVal': self.param_change(x))
        self.layout_outer.addWidget(reset_button)
        self.widget_container = QWidget()
        self.widget_container.setLayout(self.layout_outer)
        self.layout.addWidget(self.widget_container)
        self.setLayout(self.layout)

    def remove_widgets(self):
        num_widgets = self.layout_outer.count()
        for i in reversed(range(num_widgets)):
            item = self.layout_outer.itemAt(i)
            item.widget().setParent(None)
            