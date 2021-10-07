Introduction to ParticleTracker
===============================

Particle tracking can be useful for many branches of science. There are
a number of libraries available that can be used to build sophisticated tracking algorithms
specific to a particular experiment or use case. However:

1. you need to be have a reasonable level of proficiency in coding. 
2. finetuning the different stages takes quite a long time.
3. different projects have different tracking requirements: some you just need the positions as quickly as possible, some particles aren't circular, some change size with time. Hence you are likely to use different algorithms all with a different interface.
4. visualising the results requires writing more code
5. why reinvent the wheel every time you start a new project, its likely that the novel bits you want to add are a small fraction of the overall process.

Based on a desire to address many of these issues we came up with ParticleTracker. ParticleTracker
is a fully gui based particle tracking software that requires minimal (or in some cases no) programming experience. There
are faster particle tracking codes, better particle tracking codes but often you just want something
that is easy to setup and produces good results in a sensible amount of time. A lot of that is about
integrating different tools and packaging them so they can be used easily and intuitively. 

ParticleTracker incorporates several different tracking algorithms with a standard interface to help make it quick and easy to 
setup different particle tracking projects. Depending on what you want to achieve this should be possible without
any coding ability. On the other hand we've also designed the project so that you can easily add 
to and extend the code. Importantly however, you are just coding the bit that needs your novel input.

Reporting Issues
----------------

We aim to test this software against the testdata described in the tutorials however bugs do slip through. 
If you become aware of an issue please report it https://github.com/MikeSmithLabTeam/particletracker/issues 


Citing ParticleTracker
----------------------

ParticleTracker was created by Mike Smith and James Downs and is offered as open source software which is free for you
to use. If you use this software for any academic publications please cite this work using the following paper:

"ParticleTracker: a gui based particle tracking software" Journal of Open Source Software (2021), M.I. Smith, J.G. Downs."

ParticleTracker also relies on two other libraries. Trackpy is used not only for the "trackpy" tracking method but also
for the linking algorithm. You should therefore also cite this project (https://zenodo.org/record/4682814#.YVcuc9rMLIU). 

OpenCV is used for the contours and hough circles
tracking methods and the annotation.