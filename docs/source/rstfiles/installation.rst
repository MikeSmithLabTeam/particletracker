Installation and Getting Started
================================

Installation
------------

You have 3 options:

1. Installing just to use the gui or batch processing (start here if you are new to python)

Even if you know no python you should have no problems setting this up with 
the instructions below and this should run on any system. It can be run with 2 lines of code! 
If you encounter problems please report them via the `issues tracker<https://github.com/MikeSmithLabTeam/particletracker/issues>` on the github page

The software should work on all operating systems (Windows, Linux, Mac). It has only been thoroughly tested on Windows and Ubuntu Linux.

To install here is a step by step recommended guide to setting things up. In
case you are coming to this new to python or new to programming we provide the steps in a lot of detail.
If you are comfortable in python skip through! 

- Make sure you have `git installed <https://git-scm.com/downloads>`` 
- Install `UV <https://docs.astral.sh/uv/getting-started/installation/>

Check that uv is in your path by opening a terminal and typing `uv --version`. 
If you get an error that uv is not found then you will need to add it to your path. The instructions for this depend on your operating system but are easily found with a google search.

Navigate to the folder you want to install particletracker in and type:

- uv init
- uv add git+https://github.com/mikesmithlabteam/particletracker.git
- uv sync

That's the installation finished. Now whenever you want to run it, in the terminal 
from the same folder type:

- uv run python
- from particletracker import track_gui
- track_gui()

You should see a dialogue open, which means everything is working.

On Windows we sometimes ran into an error aconcerning the hdflib that 
can be resolved by installing the Microsoft Visual Studio Build tools. Once you've
installed them restart computer, open anaconda terminal, activate environment (step 2 above)
Rerun the final command above. Install the `build tools<https://visualstudio.microsoft.com/visual-cpp-build-tools/ >`


2. Installing with a view to editing the code or running the tests

Clone the repository to your computer using git:

- `git clone https://github.com/MikeSmithLabTeam/particletracker.git`
- `cd particletracker`
- `uv sync --editable .`

3. Installing using Docker




Verifying the installation
--------------------------

If you `git clone` the github repo you can verify the installation is working correctly by:

- `uv run pytest` from the root directory of the repository.

The testdata is included with the repository under testdata.

Alternatively, if you did the quick installation is working correctly you should read the getting started section which 
explains how to launch the software. Once you have done 
this there are 5 example videos which also act as tutorials which should enable you to verify and test the core functionality of the software.

To download the testdata go to: https://download-directory.github.io/
and paste in the following URL: https://github.com/MikeSmithLabTeam/particletracker/tree/master/testdata

This will create a zip folder containing all the testdata and files needed for the tutorials.


