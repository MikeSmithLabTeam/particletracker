from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qtwidgets.draggable_list import MyListWidget
from ..gui.custom_combo_box import ComboBoxAndButton
from ..gui.custom_slidergroupwidgets import CollectionParamAdjustors, CropMask

class CustomTabWidget(QTabWidget):
    """
    Fairly high level widget that handles the tabbed pages structure on the rhs of the gui.
    Into this widget we build the layouts for the upper and lower sections and instantiate
    MyListWidget, ComboBoxAndButton and either CollectionParamAdjustors or CropMask.
    """

    def __init__(self, tracker, img_viewer, param_change, method_change, reboot=None, *args, **kwargs):
        super(CustomTabWidget, self).__init__()
        self.reboot=reboot
        self.img_viewer = img_viewer
        self.method_change = method_change
        self.param_change = param_change
        self.tracker=tracker
        self.param_dict = tracker.parameters

        #Methods added to top rh box
        self.list_draggable_lists = []

        #
        self.list_param_adjustors = []
        self.list_param_adjustor_layouts = []

        #ignore config and don't make a tab for it
        tab_list = list(self.param_dict.keys()).copy()[1:]
        
        if 'selected' in tab_list: 
            tab_list.remove('selected')

        for index, key in enumerate(tab_list):
            self.add_tab(QLabel(), key, index)

    def add_tab(self, widget, title, index):
        #Setup tab
        QTabWidget.addTab(self, widget, title)
        self.tabBar().setTabButton(self.tabBar().count()-1, QTabBar.LeftSide, QLabel())
        self.setTabPosition(QTabWidget.West)
        self.tab_widget_layout = QVBoxLayout()
        
        #Top RH widgets
        self.top_tab_widget_layout = QHBoxLayout()
        self.add_top_widgets(title)
        
        #Bottom RH widgets
        bottom_tab_widget_layout = QVBoxLayout()
        param_adjustors = self.add_bottom_widgets(title)
        bottom_tab_widget_layout.addWidget(param_adjustors)
        self.list_param_adjustor_layouts.append(bottom_tab_widget_layout)
        self.list_param_adjustors.append(param_adjustors)
        
        #Add layouts to tab
        self.tab_widget_layout.addLayout(self.top_tab_widget_layout)
        self.tab_widget_layout.addLayout(bottom_tab_widget_layout)
        widget.setLayout(self.tab_widget_layout)

    def add_top_widgets(self,title):
        '''Add the widgets specified by the tracker.parameters[title]
        dictionary to the tab with name title.
        The top half of the layout contains the draggable list widget, combobox
        and add button.
        The bottom half the slidergroups etc to adjust the individual parameters.
        '''
        method_list = list(self.param_dict[title][title + '_method'])
        if ('track' in title) or ('link' in title):
            self.draggable_list = MyListWidget(method_list, title=title, dynamic=False)
        else:
            self.draggable_list = MyListWidget(method_list, title=title, dynamic=True)
        self.list_draggable_lists.append(self.draggable_list)
        self.draggable_list.add_draggable_list_methods()
        self.draggable_list.listChanged.connect(self.method_change)
        combo_button = ComboBoxAndButton(title, self)
        self.top_tab_widget_layout.addWidget(self.draggable_list)
        self.top_tab_widget_layout.addWidget(combo_button)


    def add_bottom_widgets(self, title):
        if 'crop' not in title:
            self.param_adjustors = CollectionParamAdjustors(title, self.param_dict[title], self.param_change)                                       
        else:
            self.param_adjustors = CropMask(title, self.param_dict[title],
                                            self.param_change, self.img_viewer)
        
        return self.param_adjustors


    '''---------------------------------------------------------------------------------------------------------------
    Call back functions
    -------------------------------------------------------------------------------------------------------------------   
    '''

    @pyqtSlot(int)
    def update_lock_state(self, max_locked_index):
        """When an icon on the menu is locked by right clicking
        a signal is sent from the CustomButton in menubar.py to this
        slot. The slot locks the tabs associated with the parameters on 
        RH side of page."""
        for index in range(self.count()):
            if max_locked_index == -1:
                #Unlock everything
                self.setTabEnabled(index, True)
            elif index < (max_locked_index + 3):
                #Lock tabs clicked on and earlier
                self.setTabEnabled(index, False)
            else:
                #Unlock later tabs
                self.setTabEnabled(index, True)

        