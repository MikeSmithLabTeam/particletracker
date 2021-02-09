Installation
============

We recommend creating a conda environment

- conda install -c anaconda pyqt
- conda install -c anaconda git
- pip install git+https://github.com/MikeSmithLabTeam/particletracker

Troubleshooting

- When installing there appears to be a bug that affects the pandas HDFSTore.
This can be resolved by: pip uninstall pytables, and then: conda install -c anaconda pytables

-On Windows we ran into an error that seemed to require the installation of the 
Microsoft Visual Studio Build tools. These can be installed from here:

https://visualstudio.microsoft.com/visual-cpp-build-tools/ 


to upgrade use:

- pip install --upgrade git+https://github.com/MikeSmithLabTeam/particletracker

