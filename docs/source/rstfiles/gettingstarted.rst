How do you start?
=================

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

Once you have done these examples there is also a jupyter notebook in the testdata folder which
helps explain the format of the output data and shows you how to manipulate it to extract the data
you want. 

- Working with the data

Extending the functionality
---------------------------

Finally, if you require something more complicated and are reasonably comfortable coding in python 

- Structure of the software
- Adding your own methods


