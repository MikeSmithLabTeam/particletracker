Data flow map
=============

Inside the _temp folder created in your data folder you will find the following files:

_temp.parquet is always data from a single frame and is overwritten at each stage
_track.parquet, _link.parquet, _postprocess.parquet contain data up to the current stage of processing that concerns the whole movie.

live processing is triggered by self.update_viewer in main_gui
This in turn is triggered when parameters, frames, buttons etc are changed. Most of these are linked to slots in the MainWindow which in turn call self.update_viewer.

update_viewer calls self.tracker.process. If f_index=None you are asking to process the whole movie. If f_index=frame_number you are asking to process single frame. locked_part is the option that tells you to draw from a preprocessed stage of the whole movie rather than the temporary file.


Initial start up:
=================

_temp folder created
--> Attempt to process stored in movie_temp.parquet - (check)

Change to ParticleTracker:
==========================

--> Attempt to process stored in movie_temp.parquet - check
--> Regardless of linking type the no_linking is used which creates arbitrary particle numbers for the frame under consideration. (check)

Process whole movie:
====================
--> All frames are tracked --> output _track.parquet
--> All frames are linked using trackpy or not linked meaning arbitrary particle numbers are created but there will not be usable trajectories --> output _link.parquet - check
--> If postprocess methods are not used _link.parquet is copied to _postprocess.parquet (check) if they are then the postprocessing step is done by analysing each frame and outputting. (check)
--> Video is annotated (check)
--> _postprocess.parquet is copied to the same dir as original movie and renamed. Params file also copied to _expt.param. (check)
--> Data in temp can be cleaned up using dustbin. (check)

Partial processing and lock:
============================
--> stages can only be locked if prerequisite files exist. eg linking requires _track.parquet. (check)
--> Locked stage eg link means previous data read from whole movie file e.g _track.parquet and outputted to _temp.parquet in live mode. (check)
--> If stage is locked and whole movie process button clicked the data read from previous stage eg _track.parquet and output to _link.parquet. The rest of the process continues as normal.

Pandas View:
============
--> In normal live processing, Pandas reads from _temp.parquet and outputs there as well
--> If stage is locked??????!!!!!!





