import os
import shutil
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
    """These are a set of buttons on the menubar used for stage by stage processing"""
    buttons=[None,None,None,None,None]
    extension=('_track.hdf5',
               '_link.hdf5',
               '_postprocess.hdf5')
    locked_part=-1# This is the highest button number index that is locked. -1 means nothing locked.
    # A signal that indicates the new value. It is fed the CustomButton.locked_part
    lockButtons = pyqtSignal(int) 

    def __init__(self, resources_dir, icon_filename, vid_filename=None, part=None):
        super().__init__(parent=None)
        self.part=part
        self.path, self.filename = os.path.split(vid_filename)
        self.lock=False    # Is the button currently locked    
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
        sender = self 
        if self.check_files_exist(sender.part):
            #Prevents you from trying to run something that requires files from previous stage.
            if sender.part == 4:
                super().mousePressEvent(event)
                #reset everything
                self.clean_up()
                
            elif event.button() == Qt.LeftButton:
                #LH button is used to process that stage.
                if not sender.isChecked():
                    super().mousePressEvent(event) 
            elif event.button() == Qt.RightButton:
                #RH button is used to lock stages up to and including current one.
                if sender.isChecked():
                    for i in range(sender.part,len(CustomButton.buttons)):
                        self.unlock_part(i)
                    CustomButton.locked_part = sender.part - 1
                    print('a',CustomButton.locked_part)
                else:
                    for i in range(0,sender.part+1):
                        self.lock_part(i)
                    CustomButton.locked_part = sender.part
                self.lockButtons.emit(CustomButton.locked_part)
        else:
            msg=QMessageBox()
            msg.setText("You haven't run the previous stages so this is not yet allowed.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


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
        #Trying to annotate requires _postprocess.hdf5
        if part >=3:
            prerequisite_files_ok = prerequisite_files_ok and os.path.exists(self.path + '/_temp/' + self.filename[:-4] + CustomButton.extension[2])
        return prerequisite_files_ok
    
    def clean_up(self):
        """clean_up

        This will copy final files (an hdf5 of tracking data and an annotated video) to folder containing video. It will then delete the _temp folder
        """
        try:
            postprocess_datafile = self.path + '/_temp/' + self.filename[:-4] + CustomButton.extension[2]
            output_datafile = self.path + self.filename[:-4] + '.hdf5'
            temp_folder = self.path + '/_temp'

            shutil.move(postprocess_datafile, output_datafile)
            shutil.rmtree(temp_folder)

            for i in range(sender.part,5):
                self.unlock_part(i)
            CustomButton.lock_part = None

        except Exception as e:
            print(f"Error during file cleanup: {str(e)}")
            
        

                
