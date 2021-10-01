
Welcome to ParticleTracker's documentation!
==================================================


Standard use
------------
.. toctree::
   :maxdepth: 2

   rstfiles/introduction
   rstfiles/installation
   rstfiles/gettingstarted
   rstfiles/overview
   rstfiles/examples
   rstfiles/batchprocessing


Extending the software
----------------------
.. toctree::
   :maxdepth: 1

   rstfiles/extending/extending
   rstfiles/extending/keyfiles
  
Reference
---------
.. toctree::
   :maxdepth: 1

   rstfiles/reference/launch_tracking.rst
   rstfiles/reference/preprocess_ref.rst
   rstfiles/reference/track_ref
   rstfiles/reference/postprocess_ref.rst
   rstfiles/reference/annotate_ref.rst

Reporting Issues
----------------

We aim to test this software against the testdata described in the tutorials however bugs do slip through. 
If you become aware of an issue please report it https://github.com/MikeSmithLabTeam/particletracker/issues 


Citing ParticleTracker
----------------------

ParticleTracker was created by Mike Smith and James Downs and is offered as open source software which is free for you
to use. If you use this software for any academic publications please cite this work using the following paper:



ParticleTracker also relies on two other libraries. Trackpy is used not only for the "trackpy" tracking method but also
for the linking algorithm. You should therefore also cite this project (). 

OpenCV is used for the contours and hough circles
tracking methods and the annotation.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
