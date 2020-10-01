Extending the functionality
===========================
The software is structured to help extension of the code.
Most steps in the tracking process contain an __init__.py and a
processstep_methods.py

Opening the methods module you will see all methods take the same
inputs and give the same outputs. Parameters can be passed to the function
by writing them into the .param dictionary (see key files). So a parameter
for a function in annotation_methods will be retrieved by

method_key = get_method_key('var_label', call_num=call_num)
var_column=parameters[method_key]['var_column']

where parameters is the appropriate section of the dictionary.
The purpose of get_method_key is that you may want to use the method
multiple times hence there is a call_num. If you invoke "circles" and then
invoke "circles" again this will be assigned the key name "circles*1". A third
call would be "circles*2".

track also contains an additional "intensity_methods" module. Once the tracking
methods have tracked all the particles if "get_intensities" is not False a method
is called from this module. If you want to call "mean_intensity" write this in place
of the False and it will call the function mean_intensity in this module.

The code finds the bounding rectangle around each particle in turn. It then masks
those pixels not part of the particle and sends this small image to the corresponding
intensity_method. The image is grayscale. You can then process this as required and return
a single value which will be stored in the "intensities" column of the dataframe.
