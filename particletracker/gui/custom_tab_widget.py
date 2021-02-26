from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ..gui.custom_drag_drop_list import MyListWidget
from ..gui.custom_combo_box import ComboBoxAndButton
from ..gui.custom_slidergroupwidgets import CollectionParamAdjustors, CropMask

class CheckableTabWidget(QTabWidget):
    checkBoxChanged = pyqtSignal(int)

    checkBoxList = []
    def __init__(self, tracker, img_viewer, param_change, method_change, reboot=None, **kwargs):
        super(CheckableTabWidget, self).__init__()
        self.reboot=reboot
        self.img_viewer = img_viewer
        self.method_change = method_change
        self.param_change = param_change
        self.tracker=tracker
        self.param_dict = tracker.parameters

        #Contains all the draggable list widgets
        self.list_draggable_lists = []
        self.list_param_adjustors = []
        self.list_param_adjustor_layouts = [] #Each item is the bottom_tab_widget_layout on an individual tab
        for index, key in enumerate(list(self.param_dict.keys())):
            self.add_tab(QLabel(), key, index)

    def add_tab(self, widget, title, index):

        QTabWidget.addTab(self, widget, title)
        checkBox = QCheckBox()
        checkBox.setCheckable(True)

        #The default value for the postprocess checkstate is set when tracker is opened from gui.open_tracker()
        # in PTProject. Here we just set the opening default of the ticked tab in the gui.
        if (title == 'postprocess') or (title == 'annotate'):
            checkBox.setCheckState(Qt.Unchecked)
        else:
            checkBox.setCheckState(Qt.Checked)
        checkBox.title = title

        self.tabBar().setTabButton(self.tabBar().count()-1, QTabBar.LeftSide, checkBox)
        self.setTabPosition(QTabWidget.West)
        checkBox.stateChanged.connect(lambda x, title=checkBox.title : self.emitStateChanged(x,title))

        self.tab_widget_layout = QVBoxLayout()
        self.top_tab_widget_layout = QHBoxLayout()
        self.add_top_widgets(title)
        self.tab_widget_layout.addLayout(self.top_tab_widget_layout)
        bottom_tab_widget_layout = QVBoxLayout()
        self.list_param_adjustor_layouts.append(bottom_tab_widget_layout)
        param_adjustors = self.add_bottom_widgets(title)
        bottom_tab_widget_layout.addWidget(param_adjustors)
        self.list_param_adjustors.append(param_adjustors)
        self.tab_widget_layout.addLayout(bottom_tab_widget_layout)
        widget.setLayout(self.tab_widget_layout)

    def add_top_widgets(self,title):
        '''Add the widgets specified by the tracker.parameters[title]
        dictionary to the tab with name title.
        The top half of the layout contains the draggable list widget, combobox
        and add button.
        The bottom half the slidergroups etc to adjust the individual parameters.
        '''
        if ('track' in title) or ('link' in title):
            self.draggable_list = MyListWidget(self, self.method_change, self.param_dict, title,  dynamic=False)
        else:
            self.draggable_list = MyListWidget(self, self.method_change, self.param_dict, title, dynamic=True)
        self.list_draggable_lists.append(self.draggable_list)
        self.draggable_list.add_draggable_list_methods()
        self.draggable_list.listChanged.connect(self.method_change)
        combo_button = ComboBoxAndButton(title, self)
        self.top_tab_widget_layout.addWidget(self.draggable_list)
        self.top_tab_widget_layout.addWidget(combo_button)

    def disable_tabs(self, index, enable=True):
        self.tabBar().setTabEnabled(index, enable)

    def add_bottom_widgets(self, title):
        if 'crop' not in title:
            self.param_adjustors = CollectionParamAdjustors(title, self.param_dict[title], self.param_change)
                                                 
        else:
            self.param_adjustors = CropMask(title, self.param_dict[title],
                                            self.param_change, self.img_viewer)
        
        return self.param_adjustors

    #def update_tracker_object(self, parameters):
    #    self.param_dict = parameters

    '''---------------------------------------------------------------------------------------------------------------
    Call back functions
    -------------------------------------------------------------------------------------------------------------------   
    '''
    def isChecked(self, index):
        return self.tabBar().tabButton(index, QTabBar.LeftSide).checkState() != Qt.Unchecked

    def emitStateChanged(self,check_state, title):
        setattr(self.tracker, title + '_select',check_state == Qt.Checked)
        self.checkBoxChanged.emit(1)
        #self.param_change()
