Extending the functionality
===========================
The software is structured to help extension of the code be really simple.
To extend any part of the software you need to do two things:
1. Add a function to the user_methods.py file in the top level of the particletracker project.
2. Add an appropriate entry to a .param file

To illustrate how to extend the software we use an example which is pretty 
much the same regardless of which part of the software you wish to extend.
Lets say we have a new postprocessing method which we want to implement.

1. Add a function to user_methods.py
------------------------------------
Open user_methods.py where you will find templates for the different sections.
We have stripped out all the comments that are put there to guide you to save space. The 
Docstrings in these examples explain what inputs and outputs your function needs to work.
You then write whatever code is required.

.. code-block::python
def postprocessor_method_name(data, f_index=None, parameters=None, call_num=None):
    try:
        method_key = get_method_key('postprocessor_method_name', call_num=call_num)
        params = parameters['postprocess'][method_key]
        """
        Write the body of your code
        """
        return df
    except Exception as e:
        raise PPMethodNameError(e)
code

There is also a matching exception which you need to also copy. Make this exception name unique
and match the raised Exception above:

.. code-block::python
class PPMethodNameError(PostprocessorError):
    """Implement this custom exception."""
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'specific error message to show user in status bar'
        self.e=e
code

2. Add an entry to the dictionary
---------------------------------
Open the file particletracker.general.param_file_creator. Inside this file there
is a multiply nested dictionary that controls the behaviour of the particletracker.

Expand the "postprocess" dictionary. Add a new key to this dictionary with the same
name as given to the function above and a value that is also a dictionary containing
all the parameters needed.

.. code-block::python
postprocess = {postprocess_method:(smooth,),
                'smooth':{'column_name':'y',
                          'output_name':'y_smooth',
                          'span':[5,1,50,1],
                          'method':'default'
                         },
                'postprocessor_method_name':{'param1' : [startval, minval, maxval, step],
                                            'param2' : False,
                                            'param3' : (0,255,0)
                                            }
                    }
code

The parameters are automatically assessed to decide what gui element to create. Here param 1
will result in a slider with initial value startval and min, max and increment values as shown.
All the other values result in simple edit text boxes.

To regenerate the file you can now call create_param_file(filename.param) to create a new file 
which can be read into the gui. 


