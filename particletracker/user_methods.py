'''
All methods created in this file will be automatically imported into the different 
method sections of the software. If you want to extend the functionality add
to this file and then make a backup somewhere separate. Then in the future 
you can update the software and simply replace this file. We provide templates
below for adding to the software in each section. You should also back up the 
parameters dictionary function which is located in general.param_file_creator.py

To add an method you must create a method and a custom exception. 
The methods in a given section all take the same inputs and outputs.
'''

#Other imports as needed

from .customexceptions import *
from .general.parameters import get_method_name, get_method_key

'''
--------------------------------------------------------------------------------------
Preprocessing Methods
--------------------------------------------------------------------------------------
'''

def example_method_name(frame, parameters=None, call_num=None):
    """
    Docstring for method. Replace 'example_method_name' in function name 
    and below.

    Inputs: 

        frame from previous step
        parameters : dictionary like object (same as .param files or 
                        output from general.param_file_creator.py

        call_num   : Usually None but if multiple calls are made modifies
                     method name with get_method_key

    Output:

        returns a frame modified by the method
    """

    try:
        method_key = get_method_key('example_method_name', call_num=call_num)
        params = parameters['preprocess'][method_key]

        """
        Write the body of your code

        Each function should have a corresponding entry in the dictionary. This is created by 
        the function in general.param_file_creator.py. Add a dictionary like this

        'example_method_name':{'param_produces_slider':[startval, minval, maxval, step],
                              'basic_text_box': True,
                              'basic_text_box2': (0,255,0)
                              }

        You can access other parameters associated with your method in the dictionary like this
        params['basic_text_box']. All data is parsed so that 'None','True','False' become None, 
        True, False. '(0,0,0,2)' becomes a tuple. '1' becomes 1 and other strings remain strings. 
        If your param is a slider which has format [startval, min, max, step]then you need to 
        wrap the return value:

        value = get_param_val(params['param_produces_slider])

        """
        
        return frame
    except Exception as e:
        raise ExampleMethodNameError(e)

class ExampleMethodNameError(PreprocessorError):
    """Implement this custom exception."""
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'specific error message to show user in status bar'
        self.e=e

'''
--------------------------------------------------------------------------------------
Tracking Methods
--------------------------------------------------------------------------------------
'''


def track_method_name(preprocessed_frame, unprocessed_frame, parameters=None, call_num=None):
    """
    Docstring for method. Replace 'track_method_name' in function name 
    and below.

    Inputs:
        preprocessed_frame : the preprocessed image
        unprocessed_frame  : the original image 
        parameters         : dictionary like object (same as .param files or 
                            output from general.param_file_creator.py)
        call_num : Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Output:
        A dataframe corresponding to the particle positions / info in a single frame

    """

    try:
        method_key = get_method_key('track_method_name', call_num=call_num)
        params = parameters[method_key]
        
        """
        Write the body of your code

        Each function should have a corresponding entry in the dictionary. This is created by 
        the function in general.param_file_creator.py. Add a dictionary like this

        'example_method_name':{'param_produces_slider':[startval, minval, maxval, step],
                              'basic_text_box': True,
                              'basic_text_box2': (0,255,0)
                              }

        You can access other parameters associated with your method in the dictionary like this
        params['basic_text_box']. All data is parsed so that 'None','True','False' become None, 
        True, False. '(0,0,0,2)' becomes a tuple. '1' becomes 1 and other strings remain strings. 
        If your param is a slider which has format [startval, min, max, step]then you need to 
        wrap the return value:

        value = get_param_val(params['param_produces_slider])

       """
        
        return df
    except Exception as e:
        raise ExampleMethodNameTrackError(e)

class ExampleMethodNameTrackError(TrackError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'specific error message to show user in status bar'
        self.e=e

"""
---------------------------------------------------------------------------------------------
Postprocessing methods
---------------------------------------------------------------------------------------------
"""

def postprocessor_method_name(data, f_index=None, parameters=None, call_num=None):
    """
    Docstring for method. Replace 'postprocessor_method_name' in function name 
    and below.

    Inputs:
        data        :   The entire dataframe (ie potentially includes many frames)
        f_index     :   integer specifying the frame number of interest to which the method
                        is applied
        parameters  :   dictionary like object (same as .param files or 
                        output from general.param_file_creator.py)
        call_num    :   Usually None but if multiple calls are made modifies
                        method name with get_method_key




    """

    try:
        method_key = get_method_key('postprocessor_method_name', call_num=call_num)
        params = parameters['postprocess'][method_key]

        """
        Write the body of your code

        Each function should have a corresponding entry in the dictionary. This is created by 
        the function in general.param_file_creator.py. Add a dictionary like this

        'example_method_name':{'param_produces_slider':[startval, minval, maxval, step],
                              'basic_text_box': True,
                              'basic_text_box2': (0,255,0)
                              }

        You can access other parameters associated with your method in the dictionary like this
        params['basic_text_box']. All data is parsed so that 'None','True','False' become None, 
        True, False. '(0,0,0,2)' becomes a tuple. '1' becomes 1 and other strings remain strings. 
        If your param is a slider which has format [startval, min, max, step]then you need to 
        wrap the return value:

        value = get_param_val(params['param_produces_slider])

        """
        
        return df
    except Exception as e:
        raise PPMethodNameError(e)

class PPMethodNameError(PostprocessorError):
    """Implement this custom exception."""
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'specific error message to show user in status bar'
        self.e=e


"""
---------------------------------------------------------------------------------------------
Annotation methods
---------------------------------------------------------------------------------------------
"""

def annotate_method_name(frame, data, f, parameters=None, call_num=None):
    """
    Docstring for method. Replace 'annotate_method_name' in function name 
    and below.

    Inputs:

        frame   :   original image from movie to be annotated
        data    :   The complete dataframe with all data
        f       :   the frame index which is currently being annotated
        parameters  :   dictionary like object (same as .param files or 
                        output from general.param_file_creator.py)
        call_num    :   Usually None but if multiple calls are made modifies
                        method name with get_method_key
    
    Ouput:



    """

    try:
        method_key = get_method_key('annotate_method_name', call_num=call_num)
        params = parameters['annotate'][method_key]

        """
        Write the body of your code

        Each function should have a corresponding entry in the dictionary. This is created by 
        the function in general.param_file_creator.py. Add a dictionary like this

        'annotate_method_name':{'param_produces_slider':[startval, minval, maxval, step],
                              'basic_text_box': True,
                              'basic_text_box2': (0,255,0)
                              }

        You can access other parameters associated with your method in the dictionary like this
        params['basic_text_box']. All data is parsed so that 'None','True','False' become None, 
        True, False. '(0,0,0,2)' becomes a tuple. '1' becomes 1 and other strings remain strings. 
        If your param is a slider which has format [startval, min, max, step]then you need to 
        wrap the return value:

        value = get_param_val(params['param_produces_slider])

        """
        annotated_frame = frame # This can be deleted
        return annotated_frame
    except Exception as e:
        raise AnnotateMethodNameError(e)

class AnnotateMethodNameError(AnnotatorError):
    """Implement this custom exception."""
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'specific error message to show user in status bar'
        self.e=e
