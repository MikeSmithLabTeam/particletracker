import os
import shutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *



class CustomMenuBar(QMenuBar):
    def contextMenuEvent(self, event):
        # Override the context menu event to suppress the default behavior
        event.ignore()  # Ignore the event to prevent the default context menu from appearing

class CustomToolBar(QToolBar):
    def contextMenuEvent(self, event):
        # Override the context menu event to suppress the default behavior
        event.ignore()  # Ignore the event to prevent the default context menu from appearing

class CustomButton(QToolButton):
    """These are a set of buttons on the menubar used for stage by stage processing"""
    buttons=[None,None,None]
    extension=('_track.hdf5',
               '_link.hdf5',
               '_postprocess.hdf5')
    locked_part=-1
    # A signal that indicates the new value. It is fed the CustomButton.locked_part
    lockButtons = pyqtSignal(int) 

    def __init__(self, resources_dir, icon_filename, vid_filename=None, part=None):
        super().__init__(parent=None)
        self.part=part
        self.path, self.filename = os.path.split(vid_filename)
        self.lock=False    
        self.normal_icon = QPixmap(os.path.join(resources_dir, icon_filename))
        self.lock_icon = QPixmap(os.path.join(resources_dir, "locked.png"))       
        self.update_icons()
        CustomButton.buttons[part]=self
        CustomButton.buttons[part].setCheckable(True)
        # Add context menu policy setting
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
    
    def update_icons(self):
        self.icon=QIcon()
        self.icon.addPixmap(self.normal_icon, QIcon.Mode.Normal, QIcon.State.Off)       
        self.icon.addPixmap(self.normal_icon, QIcon.Mode.Active, QIcon.State.Off)     
        self.icon.addPixmap(self.lock_icon, QIcon.Mode.Normal, QIcon.State.On)     
        self.setIcon(self.icon)
    
    def unlock_part(self, part):
        if CustomButton.buttons[part].lock:
            CustomButton.buttons[part].setChecked(False)
            CustomButton.buttons[part].update_icons()
            CustomButton.buttons[part].lock = False
            
    def lock_part(self,part):
        if not CustomButton.buttons[part].lock:
            CustomButton.buttons[part].setChecked(True)
            CustomButton.buttons[part].update_icons()
            CustomButton.buttons[part].lock = True
       
    def mousePressEvent(self, event):
        sender = self 
        if self.check_files_exist(sender.part):
            #Prevents you from trying to run something that requires files from previous stage.
            if event.button() == Qt.MouseButton.LeftButton:
                #LH button is used to lock stages up to and including current one.
                if sender.isChecked():
                    for i in range(sender.part,len(CustomButton.buttons)):
                        self.unlock_part(i)
                    CustomButton.locked_part = sender.part - 1
                else:
                    for i in range(0,sender.part+1):
                        self.lock_part(i)
                    CustomButton.locked_part = sender.part
                self.lockButtons.emit(CustomButton.locked_part)
        else:
            msg=QMessageBox()
            msg.setText("You haven't run the previous stages so this is not yet allowed.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()


    def check_files_exist(self, part):
        """check_files_exist

        This checks that the prerequisite files for the requested operation are in place. You won't
        be able to run a stage or lock stages unless these are in place.
        """
        prerequisite_files_ok=True
        #Trying to track requires no prerequisites
        if part == 0:
            return True
        #Trying to link requires _track.hdf5
        if part >= 1:
            prerequisite_files_ok = prerequisite_files_ok and os.path.exists(self.path + '/_temp/' + self.filename[:-4] + CustomButton.extension[0])
        #Trying to postprocess requires _link.hdf5
        if part >=2: 
            prerequisite_files_ok = prerequisite_files_ok and os.path.exists(self.path + '/_temp/' + self.filename[:-4] + CustomButton.extension[1])
        return prerequisite_files_ok
    
    @classmethod
    def reset_lock(cls):
        for idx,button in enumerate(cls.buttons):
            button.unlock_part(idx)
        CustomButton.locked_part = -1





