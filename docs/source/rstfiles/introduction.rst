Introduction to ParticleTracker
===============================

Particle tracking can be useful for many branches of science. There are
a number of libraries available that can be used to build sophisticated tracking algorithms
specific to a particular experiment or use case. However:

1. you need to be have some level of proficiency in coding. 
2. finetuning the different stages takes quite a bit of playing with and could always do with speeding up.
3. different projects have different tracking requirements: some you just need the positions as quickly 
as possible, some particles aren't circular, some change size with time.
4. visualising the results requires writing more code
5. why reinvent the wheel every time you start a new project, its likely that the novel bits you 
want to add are a small fraction of the overall process.

Based on a desire to address many of these issues we came up with particletracker. ParticleTracker
is a fully gui based particle tracking software that requires minimal programming experience. It incorporates
several different tracking algorithms with a standard interface to help make it quick and easy to 
setup different particle tracking projects. Depending on what you want to achieve this should be possible without
any coding ability. On the other hand we've also designed the project so that you can easily add 
to and extend the code. Importantly however you are just coding the bit that needs your novel input.