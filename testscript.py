from particletracker import track_gui
from particletracker.general.param_file_creator import create_param_file
import particletracker

movie_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\testdata\\contours.mp4'
settings_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\particletracker\\testdata\\contours.param'
#settings_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\particletracker\\particletracker\\project\\default.param'
create_param_file(settings_filename)

track_gui(movie_filename=movie_filename,settings_filename=settings_filename)

