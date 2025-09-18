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
- Go to "https://github.com/MikeSmithLabTeam/particletracker/blob/master/particletracker.yaml"
- Download this file (its an icon on top righ with a downwards arrow) and save to your project directory
- Open a conda terminal:

On Windows type Anaconda at the windows search and then select "Anaconda Prompt"
On Linux and Mac open a terminal. 

- Navigate to your project directory: type "cd path\to\project\directory"
- Type conda env create -f particletracker.yaml
- Go make a cup of coffee.

On Windows we sometimes ran into an error at this point concerning the hdflib that 
can be resolved by installing the Microsoft Visual Studio Build tools. Once you've
installed them restart computer, open anaconda terminal, activate environment (step 2 above)
Rerun the final command above. The build tools can be installed from here:

https://visualstudio.microsoft.com/visual-cpp-build-tools/ 

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


