from PyQt5.QtCore import QTimer


"""
----------------------------------------------------------------------------------------------------
These functions pick up the error messages and display them temporarily in the status bar
----------------------------------------------------------------------------------------------------
"""

def flash_error_msg(e, self):
    #self.status_bar = QStatusBar()
    #self.setStatusBar(self.status_bar)
    self.timer = QTimer(self)
    self.timer.timeout.connect(self.reset_statusbar)#lambda x=self.status_bar:reset_statusbar(x))
    self.timer.start(5000)
    self.status_bar.setStyleSheet("background-color : red")
    self.status_bar.showMessage("There is an error: " + e.error_process + e.error_msg)    
    self.show()
    

def reset_statusbar(status_bar):
    status_bar.hide()


"""
--------------------------------------------------------------
Custom base class - used only to catch all custom exceptions
--------------------------------------------------------------
"""

class BaseError(Exception):
    def __init__(self, e):
        print(e)

"""
--------------------------------------------------------------
Custom process class - inherited by all custom method exceptions
                    provides a means to trace the location of error
--------------------------------------------------------------
"""
class ExperimentError(BaseError):
    def __init__(self, e):
        super().__init__(e)
        self.error_process = 'Experiment Error - '

class CropMaskError(BaseError):
    def __init__(self, e):
        super().__init__(e)
        self.error_process = 'Crop or Mask Error - '
        self.error_msg = 'Check the input image type you need to convert to single colour channel. Crop or Mask tools also throw error if no or wrong values inputted via selection tools'

class PreprocessorError(BaseError):
    def __init__(self, e):
        super().__init__(e)
        self.error_process = 'Preprocessing Error - '
        
class TrackError(BaseError):
    def __init__(self, e):
        super().__init__(e)
        self.error_process = 'Tracking Error - '

class LinkError(BaseError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'A common error is to set max_frame_displacement too large.'
        self.error_process = 'Linking Error  - '

class PostprocessorError(BaseError):
    def __init__(self, e):
        super().__init__(e)
        self.error_process = 'Postprocessing Error - '

class AnnotatorError(BaseError):
    def __init__(self, e):
        super().__init__(e)
        self.error_process = 'Annotating Error - '

class CsvError(BaseError):
    def __init__(self, e):
        super().__init__(e)
        self.error_process = 'Error writing to csv'