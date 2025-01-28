Installation and Getting Started
================================

Installation
------------

Even if you know no python you should have no problems setting this up with 
the instructions below and this should run on any system. It can be run with 2 lines of code! 
If you encounter problems please report them via the issues tracker on the github page

https://github.com/MikeSmithLabTeam/particletracker/issues

An additional feature of this project, is that we have tried to make extending it as easy as possible. 
It might mean as little as adding a few lines of python code into a preconfigured template.

The software should work on all operating systems (Windows, Linux, Mac). It has only been thoroughly tested on Windows 10 and Ubuntu Linux.

To install here is a step by step recommended guide to setting things up.  In
case you are coming to this new to python or new to programming we provide the steps in a lot of detail.
If you are comfortable in python skip through! 

- Download and install miniconda (https://docs.conda.io/en/latest/miniconda.html)
- Open a conda terminal:

On Windows type Anaconda at the windows search and then select "Anaconda Prompt"
On Linux and Mac open a terminal. 

- Create a conda environment by typing "conda create -n particle" where particle here is the name of an `environment`.
- Type `conda activate particle`
- conda install pytables
- conda install git
- conda install pyqt
- pip install git+https://github.com/MikeSmithLabTeam/particletracker
- pip install legacy-cgi

On Windows we sometimes ran into an error at this point concerning the hdflib that 
can be resolved by installing the Microsoft Visual Studio Build tools. Once you've
installed them restart computer, open anaconda terminal, activate environment (step 2 above)
Rerun the final command above. The build tools can be installed from here:

https://visualstudio.microsoft.com/visual-cpp-build-tools/ 

(Optional - nice way to work with the final data in a jupyter notebook) 
- conda install jupyterlab 
- conda install openpyxl

to upgrade use:

- pip install --upgrade git+https://github.com/MikeSmithLabTeam/particletracker

Once installed you will need some way to write simple code and execute it. The bare bones 
approach is to use notepad and write the few lines of code as detailed in "Getting started". Save 
the file as eg. testscript.py and then from the conda command prompt navigate to the correct folder 
and run this script using "python testscript.py". Alternatively and far better in the long run is to
install a python IDE and learn how to run code in the conda environment you've 
just created. Good IDEs include among others:

- PyCharm (https://www.jetbrains.com/pycharm/download/),
- VsCode (https://code.visualstudio.com/download)

Instructions abound on Google.

Verifying the installation
--------------------------

To verify that the installation is working correctly you should read the getting started section which 
explains how to launch the software. Once you have done 
this there are 5 example videos which also act as tutorials which should enable you to verify and test the core functionality of the software.

To download the testdata go to: https://download-directory.github.io/
and paste in the following URL: https://github.com/MikeSmithLabTeam/particletracker/tree/master/testdata

This will create a zip folder containing all the testdata and files needed for the tutorials.


