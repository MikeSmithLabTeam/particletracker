Understanding key files
=======================

Within the software we make use of several important files
- .param files
- .hdf5 files

.param files
------------
.param files are a nested set of python dictionaries. They effectively
describe all the settings for a particle tracking project. 
The testdata contains a default.param which you can modify in the software
and save. Alternatively if you are using python you can create one.
A new default param file can be created:

.. code-block::python
    from particletracker.general import param_file_creator
    filename = 'path/to/file.param'
    param_file_creator(filename)
code

The top level is a dictionary which has keys:

.. code-block::python
PARAMETERS = {
    'experiment': experiment,
    'crop': crop,
    'preprocess':preprocess,
    'track':track,
    'link':link,
    'postprocess':postprocess,
    'annotate':annotate
    }
code

One key for each key step in the tracking process. The value for
each key is another dictionary which specifies the settings for that stage.

.. code-block::python
preprocess = {
    'preprocess_method': ('grayscale','medianblur',),
    'grayscale':{},#'load_bkg_img':False,
    'threshold':{'threshold':[1,0,255,1],
                 'th_mode':[1,0,1,1]},
    'adaptive_threshold':{'block_size': [29,1,300,2],
                          'C': [-23, -30, 30, 1],
                          'ad_mode': [0, 0, 1, 1]
                          },
    }
code

Above is a slimmed down version of the preprocess dictionary but all
dictionaries are structured in the same way. The top line is always
"dictionaryname"_method:(method1, method2,). Only the methods named in
this tuple are actually active methods eg grayscale and medianblur.
Note below this there are many methods that are not listed here.
These methods are not active but they are setup with default params
so you can add them in.

For each method there is yet another dictionary. These contain
the individual parameters for each method. These can be of several types.

- [startval, min, max, step] - These types will result in a spinbox slider in the gui.
- There are strings and True, False, None which will result in edit textboxes.

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
