Data flow map
=============

_temp.hdf5 is always data from a single frame and is overwritten at each stage
_track.hdf5, _link.hdf5, _postprocess.hdf5 contain data up to the current stage of processing that concerns the whole movie.


live processing is triggered by self.update_viewer in main_gui
This in turn is triggered when parameters, frames, buttons etc are changed. Most of these are linked to slots in the MainWindow which in turn call self.update_viewer
update_viewer calls self.tracker.process. If f_index=None you are asking to process the whole movie. If f_index=frame_number you are asking to process single frame. lock_part
is the option that tells you to draw from a preprocessed stage of the whole movie rather than the temporary file.


Initial start up:
=================

_temp folder created
--> Attempt to process stored in movie_temp.hdf5 - (check)

Change to ParticleTracker:
==========================

--> Attempt to process stored in movie_temp.hdf5 - check
--> Regardless of linking type the no_linking is used which creates arbitrary particle numbers for the frame under consideration. (check)

Process whole movie:
====================
--> All frames are tracked --> output _track.hdf5
--> All frames are linked using trackpy or not linked meaning arbitrary particle numbers are created but there will not be usable trajectories --> output _link.hdf5 - check
--> If postprocess methods are not used _link.hdf5 is copied to _postprocess.hdf5 (check) if they are then the postprocessing step is done by analysing each frame and outputting. (check)
--> Video is annotated (check)
--> _postprocess.hdf5 is copied to the same dir as original movie and renamed. Params file also copied to _expt.param. (check)
--> Data in temp can be cleaned up using dustbin. (check)

Partial processing and lock:
============================
--> stages can only be locked if prerequisite files exist. eg linking requires _track.hdf5. (check)
--> Locked stage eg link means previous data read from whole movie file e.g _track.hdf5 and outputted to _temp.hdf5 in live mode. (check)
--> If stage is locked and whole movie process button clicked the data read from previous stage eg _track.hdf5 and output to _link.hdf5. The rest of the process continues as normal.

Pandas View:
============
--> In normal live processing, Pandas reads from _temp.hdf5 and outputs there as well
--> If stage is locked??????!!!!!!





