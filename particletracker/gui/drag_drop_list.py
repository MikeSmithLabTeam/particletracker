from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MyListWidget(QListWidget):

    def __init__(self, update_viewer_fn, param_dict, title, parent, *args, **kwargs):
        self.parent=parent
        self.method_list = []
        super(MyListWidget, self).__init__(*args, **kwargs)
        if title in ['track', 'link']:
            '''
            A dynamic list allow you to add and remove items. A static
            one has a maximum occupancy of 1 and can only be swapped.
            '''
            self.dynamic=False
        else:
            self.dynamic=True
        self.update_viewer_fn = update_viewer_fn
        self.param_dict = param_dict
        self.title=title
        self.item_index = 0

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setMovement(QListView.Snap)
        font=QFont()
        font.setPointSize(12)
        self.setFont(font)
        if self.dynamic:
            self.setDragEnabled(True)
            self.setDropIndicatorShown(True)
            self.setDragDropMode(QAbstractItemView.DragDrop)
            self.setDefaultDropAction(Qt.MoveAction)
        else:
            self.setDragEnabled(False)


    def add_draggable_list_methods(self, title, new_dict=None):
        try:
            if new_dict is not None:
                self.method_list = list(new_dict[title][title + '_method'])
            else:
                self.method_list = list(new_dict[title][title + '_method'])

            if self.dynamic:
                self.method_list.append('----Inactive----')
            for item in self.method_list:
                self.add_item(item, update=False)
        except:
            print('skipping value')
        return self

    def add_item(self, key, update=True):
        if not self.dynamic:
            self.takeItem(0)
        self.addItem(key)
        self.get_new_method_list()
        if update:
            self.update_dictionary()
            self.update_viewer_fn()
            self.reset_param_widgets()



    def really_ugly_fix(self):
        '''
        Bug that creates a crop_method key in top
        level of dictionary. The change seems to happen
        between a call to addItem and the press mouse
        event to pick up an item from a list and move it
        Can't find anything that should be happening in this
        window. It's incredibly ugly but can't be bothered
        to spend any more time on this!
        :return:
        '''
        if 'crop_method' in list(self.param_dict.keys()):
            self.param_dict.pop('crop_method')
        if 'preprocess_method' in list(self.param_dict.keys()):
            self.param_dict.pop('preprocess_method')

    def mousePressEvent(self, event):
        self.really_ugly_fix()
        pos = self.mapFromGlobal(QCursor.pos())
        row = self.indexAt(pos).row()
        if event.button() == Qt.RightButton:
            items = self.findItems('----Inactive----', Qt.MatchExactly)
            if self.dynamic:
                if row != self.row(items[0]):
                    self.takeItem(row)
                    self.get_new_method_list()
                    self.update_dictionary()
                    self.update_viewer_fn()
                    self.reset_param_widgets()
        else:
            super().mousePressEvent(event)


    def dropEvent(self, event):

        '''
        The logic in this method is complicated by the behaviour of
        drag and drop in PyQT5. Whilst the visible list updates correctly
        returning the list of methods ends up with 2 entries for the
        selected method at the former and new locations. We correct the returned
        list to obtain the correct behaviour.
        '''
        widget = self.currentItem()
        active_method = widget.text()
        old_method_list = self.get_new_method_list()
        old_item_index = old_method_list.index(active_method)
        super().dropEvent(event)
        new_method_list = self.get_new_method_list()
        new_item_indices = [i for i in range(len(new_method_list)) if new_method_list[i] == active_method]
        if old_item_index in new_item_indices:
            #Move method down in list
            new_method_list.pop(old_item_index)
        else:
            #Move method up in list
            new_method_list.pop(old_item_index+1)
        self.method_list = new_method_list
        self.update_dictionary()

        self.update_viewer_fn()
        self.reset_param_widgets()

    def get_new_method_list(self):
        new_method_list = []
        for index in range(self.count()):
            method = self.item(index).text()
            new_method_list.append(method)
        self.method_list=new_method_list
        return new_method_list

    def update_dictionary(self):
        if self.dynamic:
            inactive_index = self.method_list.index('----Inactive----')
            self.param_dict[self.title][self.title + '_method'] = tuple(self.method_list[:inactive_index])
            param_dict_keys = list(self.param_dict[self.title].keys())
            id = param_dict_keys.index(self.title + '_method')
            param_dict_keys.pop(id)
            '''
            When a new method is added the parameters dictionary needs 1) the tuple in
            title_method updating 2) the corresponding parameters that need to 
            be adjusted. Part 1 is done in ComboBoxAndButton.add_method_button_click() Since the starting dictionary has one entry for
            each method we copy this to a new set of parameters and append * and a number to the name of the method'''

            for method in self.param_dict[self.title][self.title + '_method']:
                if (method not in param_dict_keys):
                    self.param_dict[self.title][method] = self.param_dict[self.title][method.split('*')[0]].copy()
        else:
            self.param_dict[self.title][self.title + '_method'] = tuple(self.method_list)

    def reset_draggable_list(self, tab_index=None, new_dict=None, update=True):
        title = self.title
        for row in reversed(range(self.count())):
            self.takeItem(row)
        self.add_draggable_list_methods(title, new_dict=new_dict)
        self.update_dictionary()
        if update:
            self.update_viewer_fn()

    def reset_param_widgets(self, tab_index=None):
        if tab_index is None:
            tab_index = self.parent.tabBar().currentIndex()
        active_tab_bottom = self.parent.list_param_adjustor_layouts[tab_index]
        #Remove all param adjustor widgets
        for i in reversed(range(active_tab_bottom.count())):
            active_tab_bottom.itemAt(i).widget().setParent(None)
        title = self.parent.tabBar().tabText(tab_index)
        self.parent.add_bottom_widgets(title, active_tab_bottom)

