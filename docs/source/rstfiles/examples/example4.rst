.. _Example4:

Example 4 - Tracking Bacteria
=============================
For this example which uses contour tracking, load the video bacteria.mp4 and also load the settingsfile bacteria.param.
The settings file has a number of the steps preconfigured which hopefully by now you should
be fairly happy with. We will however comment briefly on a few key points. 

1. Absolute diff preprocessing method
    This method takes the absolute difference between the pixel intensities and a reference 
    value which can be adjusted. We've found it can be very useful in microscopy where
    features may appear brighter or darker than the background depending on whether they 
    are above or below the image plane. An alternative method which is often also useful
    is the subtract_bkg method which can be used to subtract a reference image from the current one.

2. Fill holes preprocessing method
    This works on a black and white image to fill in small enclosed holes. This can be useful
    to eliminate spurious contours. 

3. Contour Boxes postprocessing method
    This calculates the minimum bounding rectangle around a contour. It creates a number of extra
    columns: "box_cx" and "box_cy" the centres of mass of the bounding rectangle; "box_angle", "box_width", "box_length", "box_area" 
    which are all pretty much self-explanatory. 

In this example we want to introduce classifiers. Suppose we are interested in identifying bacteria 
that are isolated and those that are (potentially) stuck together. One way to do this would 
be to analyse the area of a contours bounding box. Small areas are individual bacteria. Larger
areas are bacteria potentially stuck together.

.. figure:: /resources/bacteria.png
    :width: 400
    :align: center

Using classifiers
-----------------
1. In the postprocessing tab add a "classify" method. It is important that this sits below "contour_boxes" in the list as we will use the outputs of this for the classification.
2. We add a column to perform the classification upon in column_name. In this case "box_area".
3. The output_name we call "single".
4. Add the boxes method to the annotation section.
5. Change the classifier_column to be "single"
6. If not already done check the checkboxes on both tabs to make them active. 
7. Return to the postprocess tab and adjust the upper threshold until the isolated bacteria are highlighted and not the groups. We found a value of 160 worked pretty well.
8. Add another "boxes" method to the annotation. Scroll down to boxes*1 and add "single" to the classifier_column. Now where it says classifier select False. Classifers produce a column of True or False values next to each particle which define if a particle is in or outside of a group defined by the classifier thresholds. To see the different groups we must also change the colour of one of the methods using the (B, G, R) format. Values for each colour channel range from 0 to 255.

Whilst we will not do it here it is possible to combine multiple classifiers through the logic operators also 
found in the postprocessing tab. This enables you to select a variety of different properties and combine them
to filter out just the ones you want. We will show later using the Jupyter notebook that having generated these columns
it is then relatively simple to perform calculations on a subset of the data.

Finish this example by clicking the "Process" button

:ref:`Example 5<Example 5>` 
