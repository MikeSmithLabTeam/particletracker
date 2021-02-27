Installation and Getting Started
================================

Installation
------------

There are two different options for installation. You can download and install the precompiled
executables or you can install the python code. The first method enables you to do pretty much
everything but won't allow you to add to or modify the code to do something specific to your use
case. One feature of this project is that we have tried to make extending it as easy as possible. 
It might mean as little as adding a few lines of python code into a preconfigured template. In
case you are coming to this new to python or new to programming we detail the steps in a lot of detail.
If this is like teaching you to suck eggs skip through! 

You can download and install the precompiled versions here:



To install the python version here is a step by step recommended guide to setting things up:

- Download and install miniconda (https://docs.conda.io/en/latest/miniconda.html)
- Open a conda terminal

On Windows type Anaconda at the windows search and then select "Anaconda Prompt"
On Linux and Mac open a terminal. 

- Create a conda environment by typing "conda create --name particle"
- Type "conda activate particle"
- conda install pyqt
- conda install git
- pip install git+https://github.com/MikeSmithLabTeam/particletracker
- conda install jupyterlab (Optional - nice way to work with the final data in a jupyter notebook)

- When installing there appears to be a bug that affects the pandas HDFSTore.
This can be resolved by: pip uninstall pytables, and then: conda install -c anaconda pytables

-On Windows we ran into an error that seemed to require the installation of the 
Microsoft Visual Studio Build tools. These can be installed from here:

https://visualstudio.microsoft.com/visual-cpp-build-tools/ 


to upgrade use:

- pip install --upgrade git+https://github.com/MikeSmithLabTeam/particletracker


Once installed you will need some way to write simple code and execute it. The bare bones 
approach is to use a notepad and write the few lines of code as detailed in "Getting started". Save 
the file as eg. testscript.py and then from the conda command prompt navigate to the correct folder 
and run this script using "python testscript.py". Alternatively and far better in the long run is to
install a python IDE and learn how to run code in the conda environment you've 
just created. Good IDEs include PyCharm, VsCode and many more. Instructions abound on Google.



