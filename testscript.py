from particletracker import track_gui
from particletracker.general.param_file_creator import create_param_file


#filename='/home/mike/Documents/Programming/python/ParticleTracker/particletracker/testdata/contours.mp4'
#settings_filename='/home/mike/Documents/Programming/python/ParticleTracker/particletracker/testdata/contours.param'
movie_filename = 'C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Teaching\\3rd and 4th yr lab projects\\yr4granularCharging\\processed videos\\processed videos\\09.03_uncharged_8_processed.mp4'
#movie_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\charge.mp4'
settings_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\Documents\\charge_expt.param'
#create_param_file(settings_filename)

track_gui(movie_filename=movie_filename,settings_filename=settings_filename)

