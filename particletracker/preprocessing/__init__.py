from ..preprocessing import preprocessing_methods as pm
from ..general.parameters import get_method_name
import numpy as np
from PyQt5.QtWidgets import QMessageBox

class Preprocessor:
    """
    Processes images using a list of methods in
    preprocessor parameters dictionary.
    """

    def __init__(self, parameters):
        self.parameters = parameters

    def process(self, frame):
        '''
        Preprocesses single frame
        '''
        error = False
        for method in self.parameters['preprocess']['preprocess_method']:
            if (not error):
                method_name, call_num = get_method_name(method)
                frame, error = getattr(pm, method_name)(frame, self.parameters, call_num=call_num)
            if error:
                msg=QMessageBox()
                msg.setText("We've detected an error in the preprocessing section. Often these errors arise from having an impossible order of items eg. a method that requires black and white eg. distance operating on a grayscale image. There should be some hints printed out in the command window but often it is quickest to just undo whatever you just did!")
                msg.exec_()
                break
        return frame, error

