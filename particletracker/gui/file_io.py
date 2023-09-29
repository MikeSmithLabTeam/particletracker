import os
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

IMG_FILE_EXT = ('.png','.jpg','.tiff','.JPG')

def validate_filenames(self, movie_filename, settings_filename):
    """Validate filenames

    Checks to see if None or valid filename. opens dialogues if not valid.

    Parameters
    ----------
    movie_filename : _type_
        _description_
    settings_filename : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if movie_filename is None or not os.path.isfile(movie_filename):
        movie_filename = open_movie_dialog(self)
    movie_filename = _create_wildcard_filename_img_seq(str(Path(movie_filename)))

    if settings_filename is None or not os.path.isfile(settings_filename):
        settings_filename = _create_default_settings_filepath(movie_filename)
    settings_filename = str(Path(settings_filename))

    return movie_filename, settings_filename 

def open_movie_dialog(self, movie_filename=None):
    """Called on start up if no movie filename supplied. Also called when open movie button is clicked."""
    options = QFileDialog.Options()
    #options |= QFileDialog.DontUseNativeDialog

    if movie_filename is None:
        movie_filename, _ = QFileDialog.getOpenFileName(self, 
                                                         "Open Movie", QDir.homePath(),"All files (*.*);; mp4 (*.mp4);;avi (*.avi);;m4v (*.m4v);;png (*.png);;jpg (*.jpg);;tiff (*.tiff)", options=options)
    else:
        movie_filename, _ = QFileDialog.getOpenFileName(self, 
                                                         "Open Movie",
                                                        self.movie_filename.split('.')[0],
                                                        "mp4 (*.mp4);;avi (*.avi);;m4v (*.m4v);;png (*.png);;jpg (*.jpg);;tiff (*.tiff)", options=options)

    return movie_filename
        

def _create_wildcard_filename_img_seq(movie_filename):
    """Wrangle input filenames
    
    Changes individual img to wildcard version but leaves videos unchanged
    img002.png --> img*.png
    vid001.mp4 --> vid001.mp4
    """
    if os.path.splitext(movie_filename)[1] in IMG_FILE_EXT:
        path, filename = os.path.split(movie_filename)
        filename_stub, ext = os.path.splitext(filename)
        movie_filename = os.path.join(path, ''.join([letter for letter in filename_stub if letter.isalpha()]) + '*' + ext)
    return movie_filename

def _create_default_settings_filepath(movie_filename):
    """Create default settings filepath
    
    Has same parent directory as movie and is named default.param
    """
    pathname, _ = os.path.split(movie_filename)
    settings_filename = os.path.normpath(os.path.join(pathname, 'default.param'))
    return settings_filename

"""-----------------------------------------------------------------
File input and output
-------------------------------------------------------------------"""


          


    

