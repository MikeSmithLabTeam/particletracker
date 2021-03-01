How do you start?
=================

If you installed the executable you can skip to "Building a tracking project"

The place to start is with the track_gui() function which is contained in the ParticleTracker. 
To start the tracking gui you simply need to run the following very simple script.

.. code-block::python
   from ParticleTracker import track_gui
   track_gui()
code

To run any project you will need to load a movie file or settings file. You can do this by modifying the
code above to include a filename for each:

.. code-block::python
   from ParticleTracker import track_gui
   track_gui(movie="FullPathToMovie.mp4", settings="FullPathToSettings.param")
code

This can be useful especially if you use the same settings over and over to save you having to load
it manually each time. However, if you leave either of these blank the software will enable you to select
these using a file dialogue.

Building a tracking project
---------------------------

The first thing to do is to read the overview to give you some orientation and then follow 
through the different example cases where we explain how 
to use many of the different features. This will take you from some very simple use cases
to building some more complicated cases. For most people's needs this will be sufficient. 
To follow these through you will need to download the testdata folder ( ). Inside this folder you
will find several example movies and some .param files. Each example has its own page in these docs
which will walk you through from start to finish. 

- Overview
- Example 1
- Example 2
- Example 3
- Example 4

Working with the output data
----------------------------

If you are doing a really small project and absolutely have to avoid programming it is possible
to export data as an excel file. Please bear in mind though that this is pretty clunky and that
as soon as your projects increase in file size, number of particles etc this becomes pretty much
unworkable.

A better way to work is to use a Jupyter notebook to look at the data. The installation for python
set this up. Simply open the anaconda command prompt and activate the "particle" environment.
To do this you type "conda activate particle". At the command prompt you then need to navigate to
the testdata folder. Type "cd path/to/testdata". Finally type "jupyter notebook". This will open the 
server from where you can open the data_example.ipynb file. This jupyter notebook
helps explain the format of the output data and shows you how to manipulate it to extract the data
you want. 


