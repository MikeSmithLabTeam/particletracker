from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys, os

from filehandling import BatchProcess

from .project import PTWorkflow
from particletracker.gui.main_gui import MainWindow




def track_gui(movie_filename=None, settings_filename=None):
    '''

    Parameters
    ----------
    movie: optional path to movie to process
    settings: optional path to .param settings config file

    Returns None
    -------

    '''
 

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    window = MainWindow(
        movie_filename=movie_filename,
        settings_filename=settings_filename)
    window.show()
    #Start event loop
    app.exec_()





def track_batchprocess(moviefilter, settings,
                       crop=True,
                       preprocess=True,
                       track=True,
                       link=True,
                       postprocess=True,
                       annotate=True, 
                       excel=False):
    '''

    Parameters
    ----------
    filefilter: This is a full filename including filepath which may include wildcard characters
    paramfile: This is a full filename including filepath for a .param config file

    Keyword arguments can be False or True. Determines whether this step is applied or not.

    Returns None
    -------

    '''

    for filename in BatchProcess(moviefilter):
        tracker = PTWorkflow(video_filename=filename, param_filename=settings)
        tracker.crop_select = crop
        tracker.preprocess_select = preprocess
        tracker.track_select = track
        tracker.link_select = link
        tracker.postprocess_select = postprocess
        tracker.annotate_select = annotate
        tracker.process(excel=excel)


