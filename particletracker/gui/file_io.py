import os
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

IMG_FILE_EXT = ('.png','.jpg','.tiff','.JPG')

def check_filenames(self, movie_filename, settings_filename):
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
        filename, _ = QFileDialog.getOpenFileName(self, 
                                                         "Open Movie", QDir.homePath(),"All files (*.*);; mp4 (*.mp4);;avi (*.avi);;m4v (*.m4v);;png (*.png);;jpg (*.jpg);;tiff (*.tiff)", options=options)
    else:
        filename, _ = QFileDialog.getOpenFileName(self, 
                                                         "Open Movie",
                                                        self.movie_filename.split('.')[0],
                                                        "mp4 (*.mp4);;avi (*.avi);;m4v (*.m4v);;png (*.png);;jpg (*.jpg);;tiff (*.tiff)", options=options)
    if filename:
        movie_filename = filename

    return movie_filename
        

def _create_wildcard_filename_img_seq(movie_filename):
    """When we select a single image we actually want all the images in that folder or sequence
    in order for that to happen we need a path that includes a wildcard in place of the filename details but keeps the extension"""
    """Wrangle input filenames
    
    Changes individual img to wildcard version but leaves videos unchanged
    img002.png --> *.png
    vid001.mp4 --> vid001.mp4
    """
    if os.path.splitext(movie_filename)[1] in IMG_FILE_EXT:
        path, filename = os.path.split(movie_filename)
        filename_stub, ext = os.path.splitext(filename)
        movie_filename = os.path.join(path, '*' + ext)
    return movie_filename

def open_settings_dialog(self, settings_filename=None):
    options = QFileDialog.Options()
    #options |= QFileDialog.DontUseNativeDialog
    if settings_filename is None:
        filename, _ = QFileDialog.getOpenFileName(self, "Open Settings File", '',
                                                "settings (*.param)", options=options)
    else:
        filename, _ = QFileDialog.getOpenFileName(self, "Open Settings File",
                                                            self.settings_filename.split('.')[0],
                                                            "settings (*.param)", options=options)     
    if filename:
        settings_filename = filename

    return settings_filename

def _create_default_settings_filepath(movie_filename):
    """Create default settings filepath
    
    Has same parent directory as movie and is named default.param
    """
    pathname, _ = os.path.split(movie_filename)
    settings_filename = os.path.normpath(os.path.join(pathname, 'default.param'))
    return settings_filename

def save_settings_dialog(self, settings_filename):
    options = QFileDialog.Options()
    #options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getSaveFileName(self, "Save Settings File", 
                                                       self.settings_filename.split('.')[0],
                                                        "settings (*.param)", 
                                                        options=options)
    
    if filename:
        settings_filename = filename
    
    settings_filename=settings_filename.split('.')[0] + '.param'
    return settings_filename


"""-----------------------------------------------------------------
File input and output
-------------------------------------------------------------------"""


          


    

