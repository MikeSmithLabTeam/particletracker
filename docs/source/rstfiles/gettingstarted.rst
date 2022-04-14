.. _Start:

How do you start?
=================

Every time you want to run the software you should
open the anaconda command prompt with your conda environment activated. On Windows type Anaconda at the windows search and then select "Anaconda Prompt".
On Linux and Mac open a terminal. Then type "conda activate particle" (assuming you followed our installation steps). Finally, navigate
to the folder where you will store your python scripts: "cd path\to\folder".

You could also do this within an IDE just make sure your python interpreter is running from the conda environment.

After this, the place to start is with the track_gui() function which is contained in the ParticleTracker. 
To start the tracking gui you need to write a simple python script into a file and save it with a .py extension.
The simple script looks like this:

.. code-block:: python
   
   from particletracker import track_gui
   track_gui()
   
When you run this script a dialogue will open asking you to select a video file to perform tracking on.
To save typing this in each time and perhaps select a custom set of settings you can however modify
the code above to include a video filename and a settings filename. You need to include the full path to each file:

.. code-block:: python

   from particletracker import track_gui
   track_gui(movie_filename="FullPathToMovie.mp4", settings_filename="FullPathToSettings.param")


Building a tracking project
---------------------------

The first thing to do is to read / watch the overview to give you some orientation and then follow 
through the different example cases where we explain how 
to use many of the different features. This will take you from some very simple use cases
to building some more complicated projects. For most people's needs this will be sufficient. 
To follow these through you will need to download the testdata folder. This is available from the toplevel of the github page (https://github.com/MikeSmithLabTeam/particletracker ). Inside this folder you will find several example videos and some .param settings files. Each example has its own page in these docs
which will walk you through from start to finish. 

- :ref:`Overview<Overview>`
- :ref:`Tutorial1 - Eye Tracking <Tutorial1>`
- :ref:`Tutorial2 - Diffusing Colloids <Tutorial2>`
- :ref:`Tutorial3 - Swelling Hydrogels <Tutorial3>`
- :ref:`Tutorial4 - Bacteria <Tutorial4>`
- :ref:`Tutorial5 - Birefringent Discs <Tutorial5>`
- :ref:`Tutorial7 - Tips and Tricks <Tutorial7>`

Working with the output data
----------------------------

If you are doing a really small project (and absolutely have to avoid programming!) it is possible
to export data as an excel file. Please bear in mind though that this is pretty clunky and that
as soon as your projects increase in file size ie number of frames x number of objects tracked etc 
this becomes pretty much unworkable. 

A better way to work is to use a Jupyter notebook to look at the data. The installation for python
set this up. Simply open the anaconda command prompt and activate the "particle" environment.
To do this you type "conda activate particle". At the command prompt you then need to navigate to
the testdata folder. Type "cd path\to\testdata". Finally type "jupyter notebook". This will open the 
server from where you can open the data_example.ipynb file. This jupyter notebook
helps explain the format of the output data and shows you how to manipulate it to extract the aggregated
data you probably want. 

- :ref:`Tutorial6 - Working with the final data in a Jupyter Notebook <Tutorial6>`

Other tips and Tricks
---------------------

- :ref:`Tutorial7 - Assorted tips and tricks to help you using ParticleTracker <Tutorial7>`

