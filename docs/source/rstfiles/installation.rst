Installation and Getting Started
================================

Installation
------------

There are two different options for installation. 

1. You can download and install the precompiled executables
2. You can install the python code. 

The first method enables you to do pretty much everything but won't allow you to add to or modify the code
to do something specific to your use case. You can download and install the precompiled versions for Windows and Linux here:

https://www.nottingham.ac.uk/~ppzmis/software.html

This might be a good way to test if the software fits your needs
before investing too much time, especially if you don't know any python. Due to the way its packaged the files are huge but if your computer complains you probably shouldn't
be trying to use this software on that computer anyway!

To use, download the windows or linux zip and extract to a directory. You should also download and extract testdata.zip which contains 
some example movies and parameter files which can be used to work through the tutorials. The software is packaged as a folder
so it doesn't install anything on your computer. On Windows the software can be started by double clicking on "particletracker.exe". However,
since there are a lot of files in the directory we suggest creating a shortcut somewhere sensible to make things easier. On Linux open a terminal inside the
folder. You can then type "./particletracker" to start the software. 

Whilst we have tested the software on a few different versions and computers of each operating system
this method is a little bit brittle. If you encounter problems please report them via the bug tracker on this github page. However, the python version of the software has been more carefully tested and so we would suggest that this is the default or fall back method. Even if you know no python you should have no problems setting this up with the instructions below. The python version whilst requiring more installation steps can be run with 2 lines of code. One feature of this project, which is only available,
via a python installation, is that we have tried to make extending it as easy as possible. 
It might mean as little as adding a few lines of python code into a preconfigured template.

To install the python version here is a step by step recommended guide to setting things up.  In
case you are coming to this new to python or new to programming we provide the steps in a lot of detail.
If you are comfortable in python skip through! 

- Download and install miniconda (https://docs.conda.io/en/latest/miniconda.html)
- Open a conda terminal:

On Windows type Anaconda at the windows search and then select "Anaconda Prompt"
On Linux and Mac open a terminal. 

- Create a conda environment by typing "conda create --name particle"
- Type "conda activate particle"
- conda install git
- conda install pyqt
- conda install pytables
- pip install git+https://github.com/MikeSmithLabTeam/particletracker

On Windows we sometimes ran into an error at this point concerning the hdflib that 
can be resolved by installing the Microsoft Visual Studio Build tools. Once you've
installed them restart computer, open anaconda terminal, activate environment (step 2 above)
Rerun the final command above. The build tools can be installed from here:

https://visualstudio.microsoft.com/visual-cpp-build-tools/ 

(Optional - nice way to work with the final data in a jupyter notebook) 
- conda install jupyterlab 

to upgrade use:

- pip install --upgrade git+https://github.com/MikeSmithLabTeam/particletracker


Once installed you will need some way to write simple code and execute it. The bare bones 
approach is to use a notepad and write the few lines of code as detailed in "Getting started". Save 
the file as eg. testscript.py and then from the conda command prompt navigate to the correct folder 
and run this script using "python testscript.py". Alternatively and far better in the long run is to
install a python IDE and learn how to run code in the conda environment you've 
just created. Good IDEs include among others:

- PyCharm (https://www.jetbrains.com/pycharm/download/),
- VsCode (https://code.visualstudio.com/download)

Instructions abound on Google.



