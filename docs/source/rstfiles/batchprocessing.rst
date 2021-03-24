.. _Batch:

Batch Processing files
======================

If you are using python once you have got a working .param settings file using the gui, 
you can then batch process movies using the same settings. We can specify the movies to 
process using a pattern matching moviefilter. It accepts wildcard characters. 
* replaces any continuous set of characters. ? replaces a single character.

So if you have a folder with files:

.. code-block:: python

   [movieAB001.mp4, movieGOBBLEDYGOOK001.mp4,movieAB002.mp4,movieAB003.mp4,movieAB101.mp4, movieAB001.avi]

a moviefilter = 'movie*00?.mp4' would process:

movieAB001, movieGOBBLEDYGOOK001.mp4, movieAB002.mp4 but not movieAB101.mp4, movieAB001.avi

To make use of this if you have a settings file saved with name. "mysettings.param" we just write the
following code:

.. code-block:: python

   from particletracker import track_batchprocess
   moviefilter = '/A/path/selector/movie*00?.mp4'
   settings = '/full/path/to/settings.param'
   track_batchprocess(moviefilter, settings,annotate=True)

You can optionally turn off the different steps so if you just want the data and don't want to 
produce annotated videos you could feed in the keyword argument annotate=False.
