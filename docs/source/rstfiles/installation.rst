Installation
============

We recommend creating a conda environment

- conda install -c anaconda pyqt
- conda install -c anaconda git
- pip install git+https://github.com/MikeSmithLabTeam/particletracker

to upgrade use:

- pip install --upgrade git+https://github.com/MikeSmithLabTeam/particletracker


- when installing on windows there appears to be a bug with pytables that affects the HDFSTore.
This can be resolved by pip uninstall pytables