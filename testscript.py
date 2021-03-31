#from particletracker import track_gui
#import multiprocessing
from particletracker.general.param_file_creator import create_param_file
#import particletracker

#movie_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\testdata\\colloids.mp4'



if __name__ == '__main__':
    settings_filename='C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\testdata\\colloids.param'
    create_param_file(settings_filename)

    #multiprocessing.freeze_support()
    #track_gui()

