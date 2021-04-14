Understanding key files
=======================

Within the software we make use of several important files

- .param files
- .hdf5 files

.param files
------------
.param files are a nested set of python dictionaries. They effectively
describe all the settings for a particle tracking project. When run with no arguments
the software creates a default.param on start up. Alternatively if you are using python you can create one:

.. code-block:: python

    from particletracker.general import param_file_creator
    filename = 'path/to/file.param'
    param_file_creator(filename)


The top level is a dictionary which has keys:

.. code-block:: python

    PARAMETERS = {  'experiment': experiment,
                    'crop': crop,
                    'preprocess':preprocess,
                    'track':track,
                    'link':link,
                    'postprocess':postprocess,
                    'annotate':annotate
                }


One key for each key step in the tracking process. The value for
each key is another dictionary which specifies the settings for that stage.

.. code-block:: python
    
    preprocess = {'preprocess_method': ('grayscale','medianblur',),
                'grayscale':{},
                'threshold':{'threshold':[1,0,255,1],
                'th_mode':[1,0,1,1]},
                'adaptive_threshold':{'block_size': [29,1,300,2],
                                      'C': [-23, -30, 30, 1],
                                      'ad_mode': [0, 0, 1, 1]
                                    },
                }


Above is a slimmed down version of the preprocess dictionary but all
dictionaries are structured in the same way. The top line is always
"dictionaryname"_method:(method1, method2,). Only the methods named in
this tuple are actually active methods eg grayscale and medianblur.
Note below this there are many methods that are not listed here.
These methods are not active but they are setup with default params
so you can add them in.

For each method there is yet another dictionary. These contain
the individual parameters for each method. These can be of several types.

- There are sliders with initial value startval and min, max and increment ("step") values as shown. If step is an integer eg 1 the slider will return integers. If step is a decimal eg 0.01 then the slider As a result if your value happens to be something like 1.0 you should write 1.0 and not 1.
- Dropdown options box with the values value, value2, value3 to choose between. Within the brackets all these should be strings. However value at the first position should be of the correct datatype.
- Text box which can take any value. The software recognises 'None', 'True' and 'False' as None, True and False.

These files can be saved and loaded directly within the gui to save sets of
parameters appropriate for a particular experiment. Once a suitable .param file
is created you can use this directly to batch process many files
without needing to run the gui. When a video is processed a copy of the param file is automatically
saved to the same folder with videoname.param


.hdf5 files
-----------
hdf5 files are for storing the data outputted from the tracking. These come
in two types:

1. vidname_temp.hdf5
2. vidname.hdf5

The first is the output from a single frame analysed on the fly in the gui.
This is what one is usually accessing. The second is the result from analysing
all the frames either with the "process_part" or "process". When you check the "use_part"
the software switches from using the vidname_temp.hdf5 file to the vidname.hdf5 to perform
postprocessing / annotation. This is sometimes necessary. For instance to calculate
a trajectory you must work with data from other frames. 
