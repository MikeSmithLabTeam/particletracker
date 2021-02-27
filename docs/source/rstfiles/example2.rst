Example 2. Using Contours tracking
=================================

Open track_gui and load the movie example2.mp4 and the settings file example2.param

In this example we have some setup a few initial stages as defaults in the example2.param 
hydrogel beads that change size and shape during the movie.
The contours method requires a binary image from which the different separate objects can be 
identified.

1. Crop and mask.

Some of this image for example the black regions down each edge is not needed. Use the crop 
tool as we did for example 1. Check the checkbox and then drag across the image the region of interest.
You'll notice that in each corner of the image there are some black dots which are not something
we want to track. To get rid of these we have selected mask_ellipse_invert. Invert means the mask will be 
inside the ellipse not outside.

2. Preprocess the image

Toggle the Preprocessed Image button below the main viewer to see the changes taking affect.

Add the following methods to the image in this order:
- grayscale
- medianblur
- adaptive_threshold

Our aim is to prepare the image so that the objects are nicely separated and in white. Since Our
particles are darker than the image under adaptive threshold we set ad_mode to 1. Play with the
sliders and watch the changes. Try setting C to 1 and block_size to 205. This gives a really nice 
separation. The contours method is really sensitive to separation of items. If two items are linked by 
even a thin sliver both particles will count as 1.

3. track

In the track tab select contours from the drop down list and add method. Toggle the image back to 
"Captured Image". 

To check that the objects are being found nicely in the image we now need annotation. Check the checkbox
on the tab labelled annotation. The gui places a small circle over the centroid of each tracked object.
However, since the method is finding contours change the annotation. Add a contours method from the
annotation panel and right click on the circles method to remove it. The contours are now highlighted.











