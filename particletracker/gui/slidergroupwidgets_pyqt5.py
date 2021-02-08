from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qtwidgets import QCustomSlider, QCustomTextBox, SelectAreaWidget
from ..gui.pyqt5_widgets import QModCustomTextBox

class CollectionParamAdjustors(QWidget):
    def __init__(self, param_dict, title,*args, **kwargs):
        super(CollectionParamAdjustors, self).__init__(*args, **kwargs)
        self.title = title
        self.build_widgets(title, param_dict)
        
        
    def build_widgets(self, title, param_dict):#, param_change):
        self.layout_outer = QVBoxLayout()
        for method in param_dict[title + '_method']:#methods:
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
                        slider.valueChanged.connect(lambda x=None: param_change(x))
                        vbox.addWidget(slider)
                        widget_count += 1

                    #if some other datatype display edit text boxes
                    else:
                        textbox = QCustomTextBox(title=method_param, value_=param_dict[method][method_param])
                        # Add location within dictionary as metadata
                        textbox.meta = [title, method, method_param]
                        textbox.widget = 'textbox'
                        # Signal connected to param_change slot. This is in toplevel.py
                        textbox.returnPressed.connect(lambda x=textbox.text: param_change(x))
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
                textbox.returnPressed.connect(lambda x=None: param_change(x))
                vbox.addWidget(textbox)
                widget_count += 1

            if widget_count > 0:
                group_box.setLayout(vbox)
                self.layout_outer.addWidget(group_box)
            else:
                group_box.deleteLater()     
        widget_container = QWidget()
        widget_container.setLayout(self.layout_outer)
        scroll = QScrollArea()
        scroll.setWidget(widget_container)
        scroll_layout = QVBoxLayout()
        scroll_layout.addWidget(scroll)
        self.setLayout(scroll_layout)  

    def remove_widgets(self):     
        num_widgets = self.layout_outer.count()
        for i in reversed(range(num_widgets)):
            item = self.layout_outer.itemAt(i)
            item.widget().setParent(None)
   
            
    


class CropMask(QWidget):
    valueChanged = pyqtSignal(str)

    def __init__(self, param_dict,title, methods, param_change, img_viewer, crop_mask_vid_obj, reboot=None, *args, **kwargs):
        super(CropMask, self).__init__(*args, **kwargs)
        self.reboot=reboot
        self.img_viewer=img_viewer
        self.title = title
        #self.crop_mask_vid_obj=crop_mask_vid_obj
        self.param_change=param_change
        self.methods = methods
        self.param_dict = param_dict
        self.build_widgets(title, param_dict)
        

    def build_widgets(self, title, param_dict):
        if not hasattr(self, 'layout_outer'):
            self.layout_outer = QVBoxLayout()
        
        self.layout_outer = QVBoxLayout()
        self.edit_widget_list = []
        self.active_methods = list(self.param_dict['crop_method'])

        for method in param_dict[title + '_method']:
            textbox = QModCustomTextBox(self.img_viewer, title=method, value_=str(self.param_dict[method]), checkbox=True)
            textbox.meta = [title, method]
            textbox.widget='textbox'
            textbox.returnPressed.connect(lambda x=textbox.value(): param_change(x))
            self.layout_outer.addWidget(textbox)
        reset_button=QPushButton('Reset')
        reset_button.meta = 'ResetMask'
        reset_button.clicked.connect(lambda x='DummyVal': param_change(x))
        layout_inner = QHBoxLayout()
        layout_inner.addWidget(reset_button)
        self.layout_outer.addLayout(layout_inner)
        self.setLayout(self.layout_outer)

    def remove_widgets(self):
        num_widgets = self.layout_outer.count()
        for i in reversed(range(num_widgets)):
            self.layout_outer.itemAt(i).widget().setParent(None)
        
    