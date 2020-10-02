from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from gui.drag_drop_list import MyListWidget
from gui.clickable_combo_box import ComboBoxAndButton
from gui.slidergroupwidgets_pyqt5 import Collect_SB_Slider, CollectionButtonLabels


class Color(QWidget):
    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)
        palette=self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class CheckableTabWidget(QTabWidget):
    checkBoxList = []
    def __init__(self, tracker, update_viewer, img_viewer, reboot=None, **kwargs):
        super(CheckableTabWidget, self).__init__()
        self.reboot=reboot

        self.img_viewer = img_viewer
        self.update_img = update_viewer
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
        param_adjustors = self.add_bottom_widgets(title, bottom_tab_widget_layout)
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
        self.draggable_list = MyListWidget(self.update_img, self.param_dict, title, self)
        self.list_draggable_lists.append(self.draggable_list)
        self.draggable_list.add_draggable_list_methods(title, new_dict=self.param_dict)
        combo_button = ComboBoxAndButton(title, self)
        self.top_tab_widget_layout.addWidget(self.draggable_list)
        self.top_tab_widget_layout.addWidget(combo_button)

    def disable_tabs(self, index, enable=True):
        self.tabBar().setTabEnabled(index, enable)

    def add_bottom_widgets(self, title, bottom_tab_widget_layout):
        if 'crop' not in title:
            self.param_adjustors = Collect_SB_Slider(self.param_dict[title],
                                                 self.param_dict[title][title + '_method'],
                                                 self.update_img)
        else:
            self.param_adjustors = CollectionButtonLabels(self.param_dict[title],
                                                 self.param_dict[title][title + '_method'],
                                                 self.update_img, self.img_viewer, self.tracker.cap, reboot=self.reboot)
        bottom_tab_widget_layout.addWidget(self.param_adjustors)
        return self.param_adjustors

    def update_tracker_object(self, parameters):
        self.param_dict = parameters

    '''---------------------------------------------------------------------------------------------------------------
    Call back functions
    -------------------------------------------------------------------------------------------------------------------   
    '''
    def isChecked(self, index):
        return self.tabBar().tabButton(index, QTabBar.LeftSide).checkState() != Qt.Unchecked

    def emitStateChanged(self,check_state, title):
        setattr(self.tracker, title + '_select',check_state == Qt.Checked)
        self.update_img()
