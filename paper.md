---
title: "ParticleTracker: a gui based particle tracking software"
tags:
  - Python
  - particle tracking
authors:
  - name: Mike I. Smith^[Corresponding author mike.i.smith\@nottingham.ac.uk]
    orcid: 0000-0002-8210-1264
    affiliation: "1" # (Multiple affiliations must be quoted)
  - name: James Downs
    affiliation: 1
affiliations:
  - name: School of Physics, University of Nottingham, UK, NG7 2RD
    index: 1
date: 14 April 2021
bibliography: paper.bib
---

# Summary

Tracking the motion of objects in a video is an important part of the
analysis in a diverse range of subject disciplines. It enables one to automate
the extraction of quantitative information about size, shape, motion etc. A number
<<<<<<< HEAD
of libraries exist [@Trackpy;@opencv_library] to help with this process but the code can be an entry barrier.
Even for researchers with the necessary skills it requires a significant investment
for each new project. Open source tools that can simplify and expedite this process whilst
still being flexible enough to
=======
of libraries exist [@trackpy;@opencv_library] to help with this process but the coding experience required can be an entry barrier.
Even for researchers with the necessary skills developing the code and optimising the parameters requires a significant investment for each new project. Open source tools that can simplify and expedite this process, whilst remaining flexible and easy to extend by the end user, help to make particle tracking
accessible to a broader range of researchers.
>>>>>>> 5395b00b11ee8aaa2148e605f7882586f06b9cf7

# Statement of need

`ParticleTracker` is a completely gui based particle tracking software
that implements and integrates a range of commonly needed tools to help users efficiently
develop a wide range of different types of particle tracking projects.
Though the underlying code is written in python it can be used as stand alone executables,
enabling those with little or no coding ability to make use of these tools. It therefore
provides an open source solution for new users to use particle tracking as a part of their research. At the same time the python code base is designed to make extending the project extremely simple. Extension
of each part of the code can be accomplished as simply as adding the project specific
code to a preconfigured template and adding a single dictionary to a parameter file.

`ParticleTracker` was initially designed with the needs of masters students in mind who,
in semester long projects, want to quickly move beyond writing code to track particles
and focus on the underlying science in their respective projects. Whilst the projects
are varied, the underlying tools needed are generally the same, with some small variation
that is specific to each project. The combined needs of efficiently setting up a new tracking project, a common interface for different underlying algorithms, but with the ability to easily extend some small part of it has therefore guided our design philosophy. However, as the software has developed it has become clear that the development speed, uniform interface to different underlying methods, and versatility of the project would also be useful for larger scale research projects. Especially since it can be used by those with or without significant coding experience.

# Acknowledgements

We acknowledge contributions from Nathan Smith in the early stages of this project.

# References
