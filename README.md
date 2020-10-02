# ParticleTracker

GUI Particle Tracking software

documentation
https://particle-tracker.readthedocs.io/en/latest/

github installation
To install run the following line in your environment

# labvision
Repository for managing images, videos and cameras. 

## Documentation 
    https://lab-vision.readthedocs.io/en/latest/

## Installation from github
    pip install git+https://github.com/MikeSmithLabTeam/particletracker
    
## Updating if already installed
    pip install --upgrade git+https://github.com/MikeSmithLabTeam/particletracker
    
## To add as a dependency to another pip repository
Add the following argument to setup.py setuptools.setup()

    dependency_links=['https://github.com/MikeSmithLabTeam/particletracker/tarball/repo/master#egg=package-1.0'],
