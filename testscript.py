from particletracker import track_gui
from particletracker.general.param_file_creator import create_param_file


#filename='/home/mike/Documents/Programming/python/ParticleTracker/particletracker/testdata/contours.mp4'
#settings_filename='/home/mike/Documents/Programming/python/ParticleTracker/particletracker/testdata/contours.param'

movie_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\charge.mp4'
settings_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\Documents\\test.param'
#create_param_file(settings_filename)

track_gui(movie_filename=movie_filename,settings_filename=settings_filename)

