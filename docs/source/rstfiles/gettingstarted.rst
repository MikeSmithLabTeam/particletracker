.. _Start:

How do you start?
=================

Precompiled versions
--------------------

If you installed the bundled software then in all cases open the extracted folder produced in the installation steps. On Windows the software can be started by double clicking on "particletracker.exe". However, since there are a lot of files in the directory we suggest creating a shortcut somewhere sensible to make things easier. On Linux open a terminal inside the folder. You can then type "./particletracker" to start the software. A dialogue allows you to select a video to perform tracking on. After this you can skip to "Building a tracking project" below.

Python Version
--------------

If you installed the python version, then every time you want to run the software you should
open the anaconda command prompt with your conda environment activated:

On Windows type Anaconda at the windows search and then select "Anaconda Prompt"
On Linux and Mac open a terminal. Then type "conda activate particle" (assuming you followed our installation steps). Finally, navigate
to the folder where you will store your python scripts: "cd path\to\folder"

After this, the place to start is with the track_gui() function which is contained in the ParticleTracker. 
To start the tracking gui you need to  run the following very simple script within your conda environment (see installation).

.. code-block:: python
   
   from particletracker import track_gui
   track_gui()
   
This will ask you to select a video file to perform tracking on.
To save typing this in each time and perhaps select a custom set of settings you can however modify
the code above to include a video filename and a settings filename. You need to include the full path to each file:

.. code-block:: python

   from particletracker import track_gui
   track_gui(movie_filename="FullPathToMovie.mp4", settings_filename="FullPathToSettings.param")


Building a tracking project
---------------------------

The first thing to do is to read the overview to give you some orientation and then follow 
through the different example cases where we explain how 
to use many of the different features. This will take you from some very simple use cases
to building some more complicated projects. For most people's needs this will be sufficient. 
To follow these through you will need to download the testdata folder. This is available from the toplevel of the github page (https://github.com/MikeSmithLabTeam/particletracker ) or you may have downloaded it when you downloaded the software from https://www.nottingham.ac.uk/~ppzmis/software.html. Inside this folder you will find several example videos and some .param settings files. Each example has its own page in these docs
which will walk you through from start to finish. 

- :ref:`Overview<Overview>`
- :ref:`Example1 - Eye Tracking <Example1>`
- :ref:`Example2 - Diffusing Colloids <Example2>`
- :ref:`Example3 - Swelling Hydrogels <Example3>`
- :ref:`Example4 - Bacteria <Example4>`
- :ref:`Example5 - Birefringent Discs <Example5>`
- :ref:`Example6 - Working with the final data in a Jupyter Notebook <Example6>`

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

- :ref:`Example6 - Working with the final data in a Jupyter Notebook <Example6>`

