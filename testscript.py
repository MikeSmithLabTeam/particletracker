from particletracker import track_gui
from particletracker.general.param_file_creator import create_param_file


#filename='/home/mike/Documents/Programming/python/ParticleTracker/particletracker/testdata/contours.mp4'
#settings_filename='/home/mike/Documents/Programming/python/ParticleTracker/particletracker/testdata/contours.param'

filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Work\\Programming\\particletracker\\particletracker\\testdata\\contours.mp4'
settings_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Work\\Programming\\particletracker\\particletracker\\testdata\\contours.param'


create_param_file(settings_filename)

track_gui(movie=filename,settings=settings_filename)

