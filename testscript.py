from particletracker import track_gui
from particletracker.general.param_file_creator import create_param_file
import particletracker

movie_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\testdata\\discs.mp4'
#settings_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\testdata\\eyes.param'
settings_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\particletracker\\project\\discs.param'
#create_param_file(settings_filename)

track_gui(movie_filename=movie_filename,settings_filename=settings_filename)

