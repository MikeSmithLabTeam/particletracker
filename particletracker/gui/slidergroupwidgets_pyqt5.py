from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ..gui.crop_mask import SelectAreaWidget


class Collect_SB_Slider(QWidget):
    def __init__(self, param_dict, methods, update_viewer_fn, *args, win=None, **kwargs):
        super(Collect_SB_Slider, self).__init__(*args, **kwargs)
        self.widget_list = []
        self.build_widgets(param_dict, methods, update_viewer_fn)

    def build_widgets(self, param_dict, methods, update_viewer_fn):
        #Layout containing all groupboxes
        self.layout_outer = QVBoxLayout()

        for method in methods:
            widget_count=0
            group_box = QGroupBox(method)
            vbox = QVBoxLayout()

            #Slider lists
            if isinstance(param_dict[method], dict):
                for method_param in list(param_dict[method].keys()):
                    if isinstance(param_dict[method][method_param], list):
                        vbox.addWidget(Spinbox_Slider(method_param,method, param_dict, update_viewer_fn))#
                        widget_count += 1

            #Edit Text boxes inside dictionaries
            if isinstance(param_dict[method], dict):
                for method_param in list(param_dict[method].keys()):
                    if isinstance(param_dict[method][method_param], str) \
                            or isinstance(param_dict[method][method_param], int) \
                            or isinstance(param_dict[method][method_param], float)\
                            or isinstance(param_dict[method][method_param], tuple)\
                            or isinstance(param_dict[method][method_param], type(None)):
                        vbox.addWidget(Text_Box(method_param, param_dict[method], update_viewer_fn))
                        widget_count += 1

            # Edit Text boxes as top level entries
            if isinstance(param_dict[method], str) \
                    or isinstance(param_dict[method], int) \
                    or isinstance(param_dict[method], float)\
                    or isinstance(param_dict[method], tuple)\
                    or isinstance(param_dict[method], type(None)):
                vbox.addWidget(Text_Box(method, param_dict, update_viewer_fn))#
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


class CollectionButtonLabels(QWidget):
    def __init__(self, param_dict, methods, update_fn, img_viewer, crop_mask_vid_obj, reboot=None, *args, **kwargs):
        super(CollectionButtonLabels, self).__init__(*args, **kwargs)
        self.reboot=reboot
        self.img_viewer=img_viewer
        self.crop_mask_vid_obj=crop_mask_vid_obj
        self.update_fn=update_fn
        self.methods = methods
        self.param_dict = param_dict
        layout= QVBoxLayout()
        self.crop_layout = layout
        self.edit_widget_list = []
        self.active_methods = list(self.param_dict['crop_method'])
        for method in methods:

            inner_layout = QHBoxLayout()
            if method == 'frame_range':
                layout.addWidget(Frame_Range_Box(method, param_dict, self.reboot))
            else:
                button=QPushButton(method)
                button.setCheckable(True)
            if method == 'crop_box':
                button.clicked.connect(lambda x=button.isChecked, method=button.text(): self.crop(x))
                edit = QLineEdit(method + ':' + str(self.param_dict['crop_box']))
                edit.returnPressed.connect(lambda x=edit.text, name='crop_box': self.update_crop_edit(x, method=name))
                self.edit_widget_list.append(edit)
            elif method == 'mask_polygon':
                button.clicked.connect(lambda x=button.isChecked, shape='mask_polygon': self.mask(x, shape=shape))
                edit = QLineEdit(method + ':' + str(self.param_dict['mask_polygon']))
                edit.returnPressed.connect(lambda x=edit.text, name='mask_polygon': self.update_mask_edit(x, method=name))
                self.edit_widget_list.append(edit)
                self.update_mask_edit(self.param_dict['mask_polygon'], method='mask_polygon')
            elif method == 'mask_ellipse':
                button.clicked.connect(lambda x=button.isChecked, shape='mask_ellipse': self.mask(x, shape=shape))
                edit = QLineEdit(method + ':' + str(self.param_dict['mask_ellipse']))
                edit.returnPressed.connect(lambda x=edit.text, name='mask_ellipse': self.update_mask_edit(x, method=name))
                self.edit_widget_list.append(edit)
                self.update_mask_edit(self.param_dict['mask_ellipse'], method='mask_ellipse')




            inner_layout.addWidget(button)
            inner_layout.addWidget(edit)
            layout.addLayout(inner_layout)
        button2=QPushButton('Reset')
        button2.clicked.connect(self.reset_crop)
        inner_layout = QHBoxLayout()
        inner_layout.addWidget(button2)
        layout.addLayout(inner_layout)
        self.setLayout(layout)

    def crop(self, check_state):
        self.img_viewer.canPan = not check_state
        if check_state:
            self.crop_tool = SelectAreaWidget(shape='rect', geometry=self.img_viewer.geometry)
            self.img_viewer.scene.addWidget(self.crop_tool)
        else:
            if hasattr(self, 'crop_tool'):
                self._set_crop()
                self.crop_tool.setParent(None)
                self.crop_tool.deleteLater()

    def _set_crop(self, method='crop_box'):
        x = [self.crop_tool.begin.x(),self.crop_tool.end.x()]
        y = [self.crop_tool.begin.y(), self.crop_tool.end.y()]
        x.sort()
        y.sort()
        crop_vals = ((x[0],x[1]),(y[0],y[1]))
        self.update_crop_edit(crop_vals)

    def update_crop_edit(self, crop_vals, method='crop_box'):
        if callable(crop_vals):
            crop_vals = crop_vals()
            crop_vals=crop_vals.split(':')[1]
            crop_vals = crop_vals.replace('(','')
            crop_vals = crop_vals.replace(')','')
            crop_vals = crop_vals.split(', ')
            crop_vals = ((int(crop_vals[0]),int(crop_vals[1])),(int(crop_vals[2]),int(crop_vals[3])))
        self.crop_mask_vid_obj.set_crop(crop_vals)
        self.crop_mask_vid_obj.mask_none()
        self.update_fn()

        for widget in self.edit_widget_list:
            if method in widget.text():
                widget.setText(method + ':' + str(crop_vals))
        self.param_dict['crop_box'] = tuple(crop_vals)

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
                self.update_fn()

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
                print(str(self.param_dict[method]))
                widget.setText(method + ':' + str(self.param_dict[method]))
                active_methods.append(method)
        self.param_dict['crop_method'] = tuple(active_methods)
        self._set_mask(method=method, pts=mask_vals)
        self.update_fn()

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


class Frame_Range_Box(QWidget):

    def __init__(self, param_name, param_dict, update_fn, *args, **kwargs):
        self.update_fn = update_fn
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
            self.update_fn()
        except:
            print('invalid value')




class Text_Box(QWidget):

    def __init__(self, param_name, param_dict, update_fn, *args, **kwargs):
        self.update_fn = update_fn
        self.param_dict = param_dict
        self.param_name = param_name
        text = param_dict[param_name]
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
            self.param_dict[self.param_name] = value
            self.update_fn()
        except:
            print('invalid value')

class Spinbox_Slider(QWidget):
    """
    Groupbox containing slider and spinbox in horizontal layout.
    """

    def __init__(self, param_name,method_name, param_list,update_viewer_fn, *args, **kwargs):
        """

        :param param_name: The name to be displayed for the combined widget eg frame
        :param param_list: [current value, min, max, increment]
        :param update_viewer_fn: function from gui main that updates image with new parameters
        :param args:
        :param kwargs:
        """
        self.param_name = param_name
        self.method_name = method_name
        self.update_viewer = update_viewer_fn
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
        self.update_viewer()

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

        except:
            print('Not valid input params')

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
