import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class CustomMenuBar(QMenuBar):
    def contextMenuEvent(self, event):
        # Override the context menu event to suppress the default behavior
        event.ignore()  # Ignore the event to prevent the default context menu from appearing

class CustomToolBar(QToolBar):
    def contextMenuEvent(self, event):
        # Override the context menu event to suppress the default behavior
        event.ignore()  # Ignore the event to prevent the default context menu from appearing

class CustomButton(QToolButton):
    buttons=[None,None,None,None,None]

    """Used for the single stage tracking"""
    def __init__(self, resources_dir, icon_filename, part):
        super().__init__(parent=None)
        self.part=part
        self.lock=False        
        self.normal_icon = QPixmap(os.path.join(resources_dir, icon_filename))
        self.lock_icon = QPixmap(os.path.join(resources_dir, "locked.png"))       
        self.update_icons()
        CustomButton.buttons[part]=self
    
    def update_icons(self):
        self.icon=QIcon()
        self.icon.addPixmap(self.normal_icon, QIcon.Normal, QIcon.Off)       
        self.icon.addPixmap(self.normal_icon, QIcon.Active, QIcon.Off)     
        self.icon.addPixmap(self.lock_icon, QIcon.Normal, QIcon.On)     
        self.setIcon(self.icon)
    
    def unlock_part(self, part):
        if CustomButton.buttons[part].lock:
            CustomButton.buttons[part].setChecked(False)
            CustomButton.buttons[part].setCheckable(False)
            CustomButton.buttons[part].update_icons()
            CustomButton.buttons[part].lock = False

    def lock_part(self,part):
        if not CustomButton.buttons[part].lock:
            CustomButton.buttons[part].setCheckable(True)
            CustomButton.buttons[part].setChecked(True)
            CustomButton.buttons[part].update_icons()
            CustomButton.buttons[part].lock = True
       
    def mousePressEvent(self, event):
        sender = self  # The sender is the button itself
        if self.part == 4:
            super().mousePressEvent(event) 
        elif event.button() == Qt.LeftButton:
            if not sender.isChecked():
                super().mousePressEvent(event) 
        elif event.button() == Qt.RightButton:
            if sender.isChecked():
                for i in range(self.part,5):
                    self.unlock_part(i)
            else:
                for i in range(0,self.part+1):
                    self.lock_part(i)
                
