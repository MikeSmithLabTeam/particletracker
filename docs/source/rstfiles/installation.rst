Installation and Getting Started
================================

Installation
------------

There are two different options for installation. 

1. You can download and install the precompiled executables
2. You can install the python code. 

The first method enables you to do pretty much everything but won't allow you to add to or modify the code
to do something specific to your use case. It might be a good way to test if the software fits your needs
before investing too much time. However, at its most basic level, the python version whilst requiring
more installation steps can be run with 2 lines of code. One feature of this project, which is only available,
via a python installation, is that we have tried to make extending it as easy as possible. 
It might mean as little as adding a few lines of python code into a preconfigured template.

You can download and install the precompiled versions here:



To install the python version here is a step by step recommended guide to setting things up.  In
case you are coming to this new to python or new to programming we provide the steps in a lot of detail.
If you are comfortable in python skip through! 

- Download and install miniconda (https://docs.conda.io/en/latest/miniconda.html)
- Open a conda terminal

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



