.. _Tutorial5:

Tutorial 5 - Birefringent Discs
==============================

Read below or watch the video:

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/849xglS3iIY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write;      encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> 

The final example uses a movie of birefringent rubber discs that are being compressed by a moveable barrier.
Load the movie "discs.mp4" from the testdata folder and the settings file "discs.param". This example
uses the hough tracking algorithm we looked at in example1. The parameters have been set
to provide a reasonably good tracking of the discs. 

.. figure:: /resources/discs1.png
    :width: 400
    :align: center


A number of things are worth noting in this example:

1. One of the odd things about the hough circles algorithm is that it can find circles which have centres outside the masked region. Click on the postprocess tab and move the remove_masked method below "----inactive----". You will see a number of extra circles appear at the edges, despite the fact that these are outside the masked region. Put the "remove_masked" method back (this method needs to go above the neighbours method so that the  network is calculated on the correct particles. 

2. You will see that in some frames a spurious particle appears in the upper left. It does not exist in every frame. We can therefore use the linking strategy to remove this. Setting the memory value to 0 ensures that if a particle appears and disappears it will not be counted as the same object. We can then set the "min_frame_life" to be relatively long. Consequently, these transient tracks are filtered and the particle is removed. 

3. Using postprocessing we calculate the neighbours of each particle which are shown using the networks feature in annotation. This stores a list of particle ids opposite each particle corresponding  to the neighbours. The neighbours can be calculated in two different ways. A KDTree which looks for the nearest particles and the Delaunay method which calculates the first "shell" of neighbouring particles.

get_intensities
---------------
Sometimes you want to be able to find a particle and then measure some property of the particle in the original
image. In this example as the rubber discs are compressed they become brighter due to birefringence. 
In the "track" tab the get_intensities box is by default False. However, we can enter the name of a 
function, defined in get_intensities, in this box. This function is sent a cropped and masked image of each individual particle that is
tracked. See an example in the figure below:

.. figure:: /resources/discs3.png
    :width: 100
    :align: center


Some analysis can then be performed in this function and a value returned to be stored
in the column "intensities". Similar behaviour is defined for the other tracking methods.
Contours sends each contour of an object individually with the area outside each contour masked.
Since Trackpy only defines the centre of an object it has an additional parameter that defines
the radius of a circle in pixels about this centroid to send to the get_intensities function.

Whilst the implementation is currently rather limited this can easily be extended by using the 
template defined in user_methods to analyse the details of each tracked object. 

:ref:`Tutorial 6 <Tutorial6>` 

