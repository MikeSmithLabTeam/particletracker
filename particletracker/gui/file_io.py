import os
from pathlib import Path





def open_movie_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        if self.movie_filename is None:
            movie_filename, ok = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath(),
                                                            "All files (*.*);; mp4 (*.mp4);;avi (*.avi);;m4v (*.m4v);;png (*.png);;jpg (*.jpg);;tiff (*.tiff)", options=options)
        else:
            movie_filename, ok = QFileDialog.getOpenFileName(self, "Open Movie",
                                                            self.movie_filename.split('.')[0],
                                                            "mp4 (*.mp4);;avi (*.avi);;m4v (*.m4v);;png (*.png);;jpg (*.jpg);;tiff (*.tiff)", options=options)
 
        """Convert filename to include wild card character in place of trailing numbers. 
        When read by ReadVideo it will find all imgs in a folder with same format.
        """
        movie_filename = create_wildcard_filename_img_seq(movie_filename)
        
        if ok:
            self.movie_filename = movie_filename
            return True
        else:
            return False

    def open_settings_dialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        if self.settings_filename is None:
            settings_filename, ok = QFileDialog.getOpenFileName(self, "Open Settings File", '',
                                                   "settings (*.param)", options=options)
        else:
            settings_filename, ok = QFileDialog.getOpenFileName(self, "Open Settings File",
                                                               self.settings_filename.split('.')[0],
                                                               "settings (*.param)", options=options)
        if ok:
            self.settings_filename = settings_filename
            return True
        else:
            return False


def validate_filenames(movie_filename, settings_filename):
    if not os.path.isfile(movie_filename):
        movie_filename = open_movie_dialog()
    movie_filename = _create_wildcard_filename_img_seq(str(Path(movie_filename)))

    if not os.path.isfile(settings_filename):
        settings_filename = _create_default_settings_filepath(movie_filename)
    settings_filename = str(Path(settings_filename))

    return movie_filename, settings_filename 


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


    def open_movie_click(self):
        if self.open_movie_dialog():
            self.reboot()
        
    def open_settings_button_click(self):
        if self.open_settings_dialog():
            self.reboot()       


    def save_settings_button_click(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        file_settings_name, _ = QFileDialog.getSaveFileName(self, "Save Settings File", self.settings_filename.split('.')[0],
                                                        "settings (*.param)", options=options)

        file_settings_name=file_settings_name.split('.')[0] + '.param'
        write_paramdict_file(self.tracker.parameters, file_settings_name)

    def export_to_csv_click(self):
        self.tracker.parameters['config']['csv_export'] = self.export_to_csv.isChecked()