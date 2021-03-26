.. _Start:

How do you start?
=================

If you installed the bundled software start the gui by double clicking the executable in the particletracker folder
after that you can skip to "Building a tracking project" below.

If you installed the python version, the place to start is with the track_gui() function which is contained in the ParticleTracker. 
To start the tracking gui you need to  run the following very simple script within your conda environment (see installation).

.. code-block:: python
   
   from ParticleTracker import track_gui
   track_gui()
   
This will ask you to select a video file to perform tracking on and load some default settings. 
To save typing this in each time and perhaps select a custom set of settings you can however modify
the code above to include a filename for each where you need to include the full path to each file:

.. code-block:: python

   from ParticleTracker import track_gui
   track_gui(movie_filename="FullPathToMovie.mp4", settings_filename="FullPathToSettings.param")


Building a tracking project
---------------------------

The first thing to do is to read the overview to give you some orientation and then follow 
through the different example cases where we explain how 
to use many of the different features. This will take you from some very simple use cases
to building some more complicated cases. For most people's needs this will be sufficient. 
To follow these through you will need to download the testdata folder ( ). Inside this folder you
will find several example movies and some .param files. Each example has its own page in these docs
which will walk you through from start to finish. 

- :ref:`Overview<Overview>`
- :ref:`Example1<Example1>`
- :ref:`Example2<Example2>`
- :ref:`Example3<Example3>`
- :ref:`Example4<Example4>`
- :ref:`Example5<Example5>`

Working with the output data
----------------------------

If you are doing a really small project (and absolutely have to avoid programming!) it is possible
to export data as an excel file. Please bear in mind though that this is pretty clunky and that
as soon as your projects increase in file size ie number of frames x number of objects tracked etc 
this becomes pretty much unworkable. 

A better way to work is to use a Jupyter notebook to look at the data. The installation for python
set this up. Simply open the anaconda command prompt and activate the "particle" environment.
To do this you type "conda activate particle". At the command prompt you then need to navigate to
the testdata folder. Type "cd path/to/testdata". Finally type "jupyter notebook". This will open the 
server from where you can open the data_example.ipynb file. This jupyter notebook
helps explain the format of the output data and shows you how to manipulate it to extract the aggregated
data you probably want. 



