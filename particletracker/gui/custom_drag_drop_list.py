from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MyListWidget(QListWidget):   
    listChanged = pyqtSignal(tuple)

    def __init__(self, parent, method_change, param_dict, title, dynamic=True, *args, **kwargs):
        self.parent=parent
        self.dynamic=dynamic
        self.method_change = method_change
        self.param_dict = param_dict
        self.title=title
        self.method_list = list(param_dict[title][title + '_method'])
        if self.dynamic:
            self.method_list.append('----Inactive----')
        super(MyListWidget, self).__init__(*args, **kwargs)
        self.item_index = 0

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setMovement(QListView.Snap)
        font=QFont()
        font.setPointSize(12)
        self.setFont(font)
        if self.dynamic:
            self.setDragEnabled(True)
            self.setDropIndicatorShown(True)
            self.setDragDropMode(QAbstractItemView.InternalMove)
            self.setDefaultDropAction(Qt.MoveAction)
            self.setAcceptDrops(True)
        else:
            self.setDragEnabled(False)

    def add_draggable_list_methods(self):
        for item in self.method_list:
            self.add_item(item)  
        self.get_new_method_list()     

    def add_item(self, key, update=False):
        if not self.dynamic:
            self.clear()
        self.addItem(key)
        if update:
            self.get_new_method_list()        
        
    def mousePressEvent(self, event):
        pos = self.mapFromGlobal(QCursor.pos())
        row = self.indexAt(pos).row()
        if event.button() == Qt.RightButton:
            items = self.findItems('----Inactive----', Qt.MatchExactly)
            if self.dynamic:
                if row != self.row(items[0]):
                    self.takeItem(row)
                    self.send_signal()
        else:
            super().mousePressEvent(event)

    def dropEvent(self, event):
        '''
        The logic in this method is complicated by the behaviour of
        drag and drop in PyQT5. Whilst the visible list updates correctly
        returning the list of methods ends up with 2 entries for the
        selected method at the former and new locations. 
        We compare the list before and after implementing the drop event
        and correct it to remove the duplicate. Finally we return
        just the active events via the signal.
        '''
        widget = self.currentItem()
        active_method = widget.text()
        old_method_list = self.get_new_method_list()
        old_item_index = old_method_list.index(active_method)
        super().dropEvent(event)
        widget = self.currentItem()
        new_method_list = self.get_new_method_list()
        new_item_indices = [i for i in range(len(new_method_list)) if new_method_list[i] == active_method]
        if old_item_index in new_item_indices:
            #Move method down in list
            new_method_list.pop(old_item_index)
        else:
            #Move method up in list
            new_method_list.pop(old_item_index+1)
        self.method_list = new_method_list
        self.clear()
        self.add_draggable_list_methods()
        self.send_signal()

    def get_new_method_list(self):
        new_method_list = []
        for index in range(self.count()):
            method = self.item(index).text()
            new_method_list.append(method)
        self.method_list=new_method_list
        return new_method_list

    def send_signal(self):
        self.get_new_method_list()
        if self.dynamic:
            active_method_list = self.method_list[:self.method_list.index('----Inactive----')]
        else:
            active_method_list = self.method_list     
        self.listChanged.emit(tuple(active_method_list))
        

