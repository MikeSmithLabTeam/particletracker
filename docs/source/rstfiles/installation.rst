Installation
============

We recommend creating a conda environment

- conda install -c anaconda pyqt
- conda install -c anaconda git
- pip install git+https://github.com/MikeSmithLabTeam/particletracker
- When installing there appears to be a bug with Tables that affects the HDFSTore.
This can be resolved by: pip uninstall tables, and then: conda install -c anaconda pytables

to upgrade use:

- pip install --upgrade git+https://github.com/MikeSmithLabTeam/particletracker
