track_gui creates a MainWindow. This MainWindow creates a tracker object. This is done through PTWorkFlow. PTWorkFlow is the entry point for anything headless which can be run useing batchprocess (the alternative to track_gui).


#Known issue

If you try to create a video without a preprocessing method that converts the frame to single channel the tracking methods error and no video is created.


