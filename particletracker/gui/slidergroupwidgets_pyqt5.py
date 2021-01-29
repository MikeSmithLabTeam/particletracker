from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qtwidgets import QCustomSlider, QCustomTextBox, SelectAreaWidget
from ..gui.pyqt5_widgets import QModCustomTextBox

class CollectionParamAdjustors(QWidget):
    def __init__(self, param_dict, title, methods, param_change, *args, win=None, **kwargs):
        super(CollectionParamAdjustors, self).__init__(*args, **kwargs)
        self.widget_list = []
        self.build_widgets(param_dict, title, methods, param_change)

    def build_widgets(self, param_dict, title, methods, param_change):
        #Layout containing all groupboxes
        self.layout_outer = QVBoxLayout()

        for method in methods:
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
        list_widgets = self.layout_outer.findChildren()
        for widget in list_widgets:
            self.layout.removeWidget(widget)


class CropMask(QWidget):
    valueChanged = pyqtSignal(str)

    def __init__(self, param_dict,title, methods, param_change, img_viewer, crop_mask_vid_obj, reboot=None, *args, **kwargs):
        super(CropMask, self).__init__(*args, **kwargs)
        self.reboot=reboot
        self.img_viewer=img_viewer
        #self.crop_mask_vid_obj=crop_mask_vid_obj
        self.param_change=param_change
        self.methods = methods
        self.param_dict = param_dict
        layout= QVBoxLayout()
        self.crop_layout = layout
        self.edit_widget_list = []
        self.active_methods = list(self.param_dict['crop_method'])

        for method in methods:
            textbox = QModCustomTextBox(self.img_viewer, title=method, value_=str(self.param_dict[method]), checkbox=True)
            textbox.meta = [title,method]
            textbox.widget='textbox'
            textbox.returnPressed.connect(lambda x=textbox.value(): param_change(x))


            layout.addWidget(textbox)
        button2=QPushButton('Reset')
        button2.clicked.connect(self.reset_crop)
        inner_layout = QHBoxLayout()
        inner_layout.addWidget(button2)
        layout.addLayout(inner_layout)
        self.setLayout(layout)

    def crop(self, check_state):
        print('crop')
        self.img_viewer.canPan = not check_state
        if check_state:
            self.crop_tool = SelectAreaWidget(shape='rect', geometry=self.img_viewer.geometry)
            self.img_viewer.scene.addWidget(self.crop_tool)
        else:
            self.emit()
            if hasattr(self, 'crop_tool'):
                pass
                #self._set_crop()
                #self.crop_tool.setParent(None)
                #self.crop_tool.deleteLater()

    def _set_crop(self, method='crop_box'):
        x = [self.crop_tool.begin.x(),self.crop_tool.end.x()]
        y = [self.crop_tool.begin.y(), self.crop_tool.end.y()]
        x.sort()
        y.sort()
        crop_vals = ((x[0],x[1]),(y[0],y[1]))
        self.update_crop_edit(crop_vals)

    def onValueChanged(self,text: str) -> None:
        self.valueChanged.emit(text)

    def update_crop_edit(self, crop_vals, method='crop_box'):


        pass
        '''
        if callable(crop_vals):
            crop_vals = crop_vals()
            crop_vals=crop_vals.split(':')[1]
            crop_vals = crop_vals.replace('(','')
            crop_vals = crop_vals.replace(')','')
            crop_vals = crop_vals.split(', ')
            crop_vals = ((int(crop_vals[0]),int(crop_vals[1])),(int(crop_vals[2]),int(crop_vals[3])))
        self.crop_mask_vid_obj.set_crop(crop_vals)
        self.crop_mask_vid_obj.mask_none()
        #self.param_change()

        for widget in self.edit_widget_list:
            if method in widget.text():
                widget.setText(method + ':' + str(crop_vals))
        self.param_dict['crop_box'] = tuple(crop_vals)
        '''

    def mask(self,check_state, shape='rect'):
        if check_state:
            self.mask_tool = SelectAreaWidget(shape=shape, geometry=self.img_viewer.geometry,colour=QColor(10,10,250,80))
            self.img_viewer.scene.addWidget(self.mask_tool)
        else:
            if hasattr(self, 'mask_tool'):
                self._set_mask(method=shape)
                if shape == 'mask_ellipse':
                    self.update_mask_edit(self.mask_tool.ellipse_pts, method='mask_ellipse')
                elif shape == 'mask_polygon':
                    self.update_mask_edit(tuple(self.mask_tool.display_point_list), method='mask_polygon')
                self.mask_tool.setParent(None)
                self.mask_tool.deleteLater()
                #self.param_change()

    def _set_mask(self, method='rect', pts=None):
        img_coords = self.crop_mask_vid_obj.crop_vals
        img_size = (img_coords[1][1] - img_coords[1][0], img_coords[0][1] - img_coords[0][0])
        if pts is None:
            self.crop_mask_vid_obj.mask_none()
        elif 'ellipse' in method:
            self.crop_mask_vid_obj.mask_ellipse(pts)
        elif 'polygon' in method:
            self.crop_mask_vid_obj.mask_polygon(pts)

    def update_mask_edit(self, mask_vals, method='mask_ellipse'):
        if callable(mask_vals):
            #called if mask_vals is a function.
            mask_vals = mask_vals()
            mask_vals=mask_vals.split(':')[1]
            mask_vals = mask_vals.replace('(','')
            mask_vals = mask_vals.replace(')','')
            mask_vals = mask_vals.split(', ')

            if mask_vals == ['None']:
                mask_vals = None
            else:
                output = []
                for i in range(int(len(mask_vals)/2)):
                    output.append((int(mask_vals[2*i]),int(mask_vals[2*i+1])))
                mask_vals=tuple(output)
        self.param_dict[method] = mask_vals

        try:
            if 'ellipse' in method:
                self.mask_tool.ellipse_pts = mask_vals
                self.param_dict['mask_ellipse']=mask_vals
            elif 'polygon' in method:
                self.mask_tool.display_point_list = mask_vals
                self.param_dict['mask_polygon'] = mask_vals
        except:
            #Yes I know this is bad practice but I don't care right now!
            pass


        active_methods = ['crop_box']

        for widget in self.edit_widget_list:
            if method in widget.text():
                widget.setText(method + ':' + str(self.param_dict[method]))
                active_methods.append(method)
        self.param_dict['crop_method'] = tuple(active_methods)
        self._set_mask(method=method, pts=mask_vals)
        #self.param_change()

    def reset_crop(self):
        crop_vals = ((0, self.crop_mask_vid_obj.width), (0, self.crop_mask_vid_obj.height))
        self.param_dict['crop_box'] = crop_vals
        self.crop_mask_vid_obj.set_crop(crop_vals)
        self.crop_mask_vid_obj.mask_none()
        self.update_crop_edit(crop_vals)
        self.param_dict['mask_ellipse'] = None
        self.param_dict['mask_polygon'] = None
        self.crop_mask_vid_obj.reset_crop()

        try:
            self.update_mask_edit(None, method='mask_ellipse')
        except:
            pass
        try:
            self.update_mask_edit(None, method='mask_polygon')
        except:
            pass

'''
class Frame_Range_Box(QWidget):

    def __init__(self, param_name, param_dict, param_change, *args, **kwargs):
        self.param_change = param_change
        self.param_dict = param_dict
        self.param_name = param_name
        text = param_dict[param_name]
        self.datatype = type(text)
        super(Frame_Range_Box, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.label = QLabel(param_name)
        self.text_value = text
        self.edit = QLineEdit(str(text))
        self.edit.returnPressed.connect(self.value_changed)
        self.edit.setMinimumWidth(400)
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        self.setLayout(layout)

    def value_changed(self):
        try:
            self.text_value=self.edit.text()

            vals = self.text_value[1:-1].split(',')
            values = []
            for val in vals:
                values.append(int(val))
            value = tuple(values)
            self.param_dict[self.param_name] = value
            self.param_change()
        except Exception as e:
            print('invalid value')
            print(e)
'''



class Text_Box(QWidget):

    def __init__(self, param_name, method_name, param_dict, param_change, *args, **kwargs):
        self.param_change = param_change
        self.param_dict = param_dict
        self.method_name=method_name
        self.param_name = param_name
        if param_name is None:
            text = param_dict[method_name]
        else:
            text = param_dict[method_name][param_name]
        self.datatype = type(text)
        super(Text_Box, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.label = QLabel(param_name)
        self.text_value = text
        self.edit = QLineEdit(str(text))
        self.edit.returnPressed.connect(self.value_changed)
        self.edit.setMinimumWidth(400)
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        self.setLayout(layout)

    def value_changed(self):
        try:
            self.text_value=self.edit.text()
            self.datatype = type(self.text_value)
            if self.datatype == float:
                value = float(self.text_value)
            elif self.datatype == int:
                value = int(self.text_value)
            elif (self.datatype == type(None)):
                value = None
            elif self.text_value == 'None':
                value = None
            elif self.text_value == 'True':
                value = True
            elif self.text_value == 'False':
                value = False
            elif self.text_value[0] == '(':
                vals = self.text_value[1:-1].split(',')
                values = []
                for val in vals:
                    values.append(int(val))
                value = tuple(values)
            elif (self.datatype == str):
                value = self.text_value
            elif self.datatype == tuple:
                vals = self.text_value[1:-1].split(',')
                values = []
                for val in vals:
                   values.append(int(val))
                value = tuple(values)
            else:
                #If datatype is None should be picked up by this.
                value = self.text_value
            if self.param_name is None:
                self.param_dict[self.method_name] = value
                print(self.method_name)
                print(self.param_dict[self.method_name])
            else:
                self.param_dict[self.method_name][self.param_name] = value
            print(self.method_name)
            print(self.param_dict[self.method_name][self.param_name])
            self.param_change()
        except Exception as e:
            print('invalid value')
            print(e)

class Spinbox_Slider(QWidget):
    """
    Groupbox containing slider and spinbox in horizontal layout.
    """

    def __init__(self, param_name,method_name, param_list,param_change, *args, **kwargs):
        """

        :param param_name: The name to be displayed for the combined widget eg frame
        :param param_list: [current value, min, max, increment]
        :param update_viewer_fn: function from gui main that updates image with new parameters
        :param args:
        :param kwargs:
        """
        self.param_name = param_name
        self.method_name = method_name
        self.param_change = param_change
        super(Spinbox_Slider,self).__init__(*args,**kwargs)
        self.param_list = param_list
        self.param_name = param_name

        layout_inner = QHBoxLayout()
        label = QLabel(param_name)
        layout_inner.addWidget(label)

        #Slider and spinbox are linked so that they
        #always show same values.
        slider=QSlider(Qt.Horizontal)
        self.slider_range = slider.setRange
        self.slider_value = slider.setSliderPosition
        self.slider_increment = slider.setSingleStep
        layout_inner.addWidget(slider)

        spinbox = QSpinBox()

        self.spinbox_range = spinbox.setRange
        self.spinbox_value =spinbox.setValue
        self.spinbox_increment = spinbox.setSingleStep
        layout_inner.addWidget(spinbox)

        slider.sliderReleased.connect(
            lambda slider_val=slider.value: self.value_changed(slider_val)
            )
        spinbox.editingFinished.connect(
            lambda spinbox_val=spinbox.value: self.value_changed(spinbox_val)
            )
        self.setLayout(layout_inner)
        self.update_params(param_list)

    def value_changed(self, get_value):
        new_value=get_value()
        if (self.param_list[self.method_name][self.param_name][3] == 2) & (new_value % 2 == 0):
            new_value += 1
        self.param_list[self.method_name][self.param_name][0] = new_value
        self.update_params([])
        self.param_change()

    def update_params(self, param_list):
        try:
            if param_list == []:
                param_list=self.param_list
            else:
                self.param_list = param_list
            self.slider_range(param_list[self.method_name][self.param_name][1], param_list[self.method_name][self.param_name][2])
            self.slider_value(param_list[self.method_name][self.param_name][0])
            self.slider_increment(param_list[self.method_name][self.param_name][3])
            self.spinbox_range(param_list[self.method_name][self.param_name][1], param_list[self.method_name][self.param_name][2])
            self.spinbox_value(param_list[self.method_name][self.param_name][0])
            self.spinbox_increment(param_list[self.method_name][self.param_name][3])

        except Exception as e:
            print('Not valid input params')
            print(e)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            output, ok = QInputDialog.getText(self, 'Enter new range:', 'min,max')
            if ok:
                output = output.split(',')
                self.param_list[self.method_name][self.param_name][1] = int(output[0])
                self.param_list[self.method_name][self.param_name][2] = int(output[1])
                self.update_params([])
        else:
            super().mousePressEvent(event)



#One QApplication needed per application
#If you won't use command line arguments QApplication([]) also works

if __name__ == '__main__':

    test2 = {'adaptive_threshold':{'block_size': [29,1,300,2],
                          'C': [-23, -30, 30, 1],
                          'ad_mode': [0, 0, 1, 1]
                          }}

    frame = {'frame': [10,1,100,1]}


    app = QApplication([])
    key='frame'
    sb = Collect_SB_Slider(test2)
    sb.show()
    app.exec_()

#Your application won't reach here until you exit and the event loop has stopped
