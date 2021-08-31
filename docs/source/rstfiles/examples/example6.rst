.. _Example6:

Example 6 - Working with the final data in a Jupyter Notebook
=============================================================
Read below or watch the video

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/BhGaWuiPADg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write;      encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> 


If you used the precompiled executable of ParticleTracker you may not have 
set up the details described in installation for working with a Jupyter Notebook.
If you don't plan to use the python version of ParticleTracker but want to analyse the output
then follow these steps:

- Download and install miniconda (https://docs.conda.io/en/latest/miniconda.html)
- Open a conda terminal

On Windows type Anaconda at the windows search and then select "Anaconda Prompt"
On Linux and Mac open a terminal. 

- Create a conda environment by typing "conda create --name particle"
- Type "conda activate particle"
- conda install pytables

On Windows we sometimes ran into an error at this point concerning the hdflib that 
can be resolved by installing the Microsoft Visual Studio Build tools. Once you've
installed them restart computer, open anaconda terminal, activate environment (step 2 above)
Rerun the final command above. The build tools can be installed from here:

https://visualstudio.microsoft.com/visual-cpp-build-tools/ 

Then run the following command:

- conda install jupyterlab 

Whenever you want to perform some analysis you need to:

- Open the Conda command prompt as above
- Change the directory to the folder containing the Jupyter notebook. In this case we are going to use the data_examples.ipynb which is contained in the testdata folder you downloaded. Navigate within the command prompt

On windows thats "cd C:\path\to\testdata". On Mac or Linux "cd /path/to/testdata".

- Activate the particle environment by typing "conda activate particle" at the command prompt.
- Type "jupyter notebook".

This will open a browser with a listing of all the files in the testdata folder. From here you have
the option in future to open a new notebook for future projects,  but in this case we are going to open
the "data_examples.ipynb" file. This notebook gives some simple examples of how to interact with the 
data files produced by ParticleTracker. When the jupyter notebook opens you can run each small cell
sequentially by selecting the cell and then clicking the play button on the toolbar or "shift" + "enter".
