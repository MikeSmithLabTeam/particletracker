from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QStatusBar

"""
----------------------------------------------------------------------------------------------------
These functions pick up the error messages and display them temporarily in the status bar
----------------------------------------------------------------------------------------------------
"""

def flash_error_msg(e, self):
    self.status_bar = QStatusBar()
    self.setStatusBar(self.status_bar)
    self.timer = QTimer(self)
    self.timer.timeout.connect(self.status_bar.hide)#lambda x=self.status_bar:reset_statusbar(x))
    self.timer.start(5000)
    self.status_bar.setStyleSheet("background-color : red")
    self.status_bar.showMessage("There is an error: " + e.error_process + e.error_msg)    
    self.show()
    

def reset_statusbar(status_bar):
    status_bar.hide()
    #status_bar.setStyleSheet("background-color : None")
    #status_bar.clearMessage()
    #status_bar.setParent(None)
    #status_bar.deleteLater()

"""
--------------------------------------------------------------
Custom base class - used only to catch all custom exceptions
--------------------------------------------------------------
"""

class BaseError(Exception):
    def __init__(self):
        pass

"""
--------------------------------------------------------------
Custom process class - inherited by all custom method exceptions
                    provides a means to trace the location of error
--------------------------------------------------------------
"""
class ExperimentError(BaseError):
    def __init__(self):
        super().__init__()
        self.error_process = 'Experiment Error - '

class CropMaskError(BaseError):
    def __init__(self):
        super().__init__()
        self.error_process = 'Crop or Mask Error'

class PreprocessorError(BaseError):
    def __init__(self):
        super().__init__()
        self.error_process = 'Preprocessing Error - '
        
class TrackError(BaseError):
    def __init__(self):
        super().__init__()
        self.error_process = 'Tracking Error - '

class LinkError(BaseError):
    def __init__(self):
        super().__init__()
        self.error_process = 'Linking Error'

class PostprocessorError(BaseError):
    def __init__(self):
        super().__init__()
        self.error_process = 'Postprocessing Error - '

class AnnotatorError(BaseError):
    def __init__(self):
        super().__init__()
        self.error_process = 'Annotating Error - '