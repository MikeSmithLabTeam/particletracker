Installation and Getting Started
================================

Installation
------------

If you are used to python feel free to skip through. We provide a step by step setup for those who feel less confident.

This is our recommended way to install:

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



