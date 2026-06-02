import os
import glob
import re
import time
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QApplication

IMG_FILE_EXT = ('.png', '.jpg', '.tiff', '.JPG')

ROOT_DIR = Path(__file__).resolve().parents[2]

def get_data_dir():
    return Path(os.getenv("PARTICLETRACKER_DATA", ROOT_DIR / "testdata"))

def _ensure_app():
    if not QApplication.instance():
        app = QApplication([])
        return app
    return None


def get_filename(initialdir='/', title="Select File", filetypes=None):
    _app = _ensure_app()

    filter_str = ";;".join([f"{label} ({pattern})" for label, pattern in filetypes]) if filetypes else ""
    filename, _ = QFileDialog.getOpenFileName(None, title, initialdir, filter_str)
    return filename


def create_filename(initialdir='/', title="Save File", filetypes=None, append_time=False):
    _app = _ensure_app()
    filter_str = ";;".join([f"{label} ({pattern})" for label, pattern in filetypes]) if filetypes else ""
    filename, _ = QFileDialog.getSaveFileName(None, title, initialdir, filter_str)

    if append_time and filename:
        filename += datetime_stamp()
    return filename


def get_directory(initialdir='/', title="Select a directory"):
    _app = _ensure_app()
    return QFileDialog.getExistingDirectory(None, title, initialdir)


def create_directory(initialdir='/', title="Create directory", parent=None):
    """
    Opens a directory selection dialog and returns the selected path.
    """
    _app = _ensure_app()
    directory = QFileDialog.getExistingDirectory(
        parent,
        title,
        initialdir,
        QFileDialog.Option.ShowDirsOnly)
    return directory


def _create_wildcard_filename_img_seq(movie_filename):
    """
    Convert a single image filename into a wildcard expression for image sequences.
    """
    if os.path.splitext(movie_filename)[1] in IMG_FILE_EXT:
        path, filename_stub, ext = img_name_wrangle(movie_filename)
        movie_filename = os.path.join(path, filename_stub + '*' + ext)
    return movie_filename


def img_name_wrangle(filename):
    """
    Remove trailing digits or '*' from an image basename.
    """
    path, filename = os.path.split(filename)
    filename_stub, ext = os.path.splitext(filename)
    return path, re.sub(r'[*\\d]+$', '', filename_stub), ext


def _create_default_settings_filepath(movie_filename):
    """
    Create default settings filepath in the same directory as the movie.
    """
    pathname, _ = os.path.split(movie_filename)
    settings_filename = os.path.normpath(os.path.join(pathname, 'default.param'))
    return settings_filename


def check_filenames(self, movie_filename, settings_filename):
    """
    Validate filenames and open dialogs if they are missing or invalid.
    """
    if movie_filename is None or not os.path.isfile(movie_filename):
        movie_filename = open_movie_dialog(self)
    movie_filename = _create_wildcard_filename_img_seq(str(Path(movie_filename)))

    if settings_filename is None or not os.path.isfile(settings_filename):
        settings_filename = _create_default_settings_filepath(movie_filename)
    settings_filename = str(Path(settings_filename))

    return movie_filename, settings_filename


def open_movie_dialog(self, movie_filename=None):
    """
    Open a movie selection dialog.
    """
    if movie_filename is None:
        initial_dir = str(get_data_dir())
    else:
        initial_dir = os.path.dirname(self.movie_filename)

    filename, _ = QFileDialog.getOpenFileName(
        self,
        "Open Movie",
        initial_dir,
        "All files (*.*);; mp4 (*.mp4);; avi (*.avi);; m4v (*.m4v);; png (*.png);; jpg (*.jpg);; tiff (*.tiff)"
    )

    if filename:
        movie_filename = _create_wildcard_filename_img_seq(filename)

    return movie_filename


def open_settings_dialog(self, settings_filename=None):
    """
    Open a settings file selection dialog.
    """
    if settings_filename is None:
        initial_dir = str(get_data_dir())
    else:
        initial_dir = os.path.dirname(self.settings_filename)

    filename, _ = QFileDialog.getOpenFileName(
        self,
        "Open Settings File",
        initial_dir,
        "settings (*.param)"
    )

    if filename:
        settings_filename = filename

    return settings_filename


def save_settings_dialog(self, settings_filename):
    """
    Open a save dialog for settings files.
    """
    if settings_filename is None:
        initial_dir = str(get_data_dir())
    else:
        initial_dir = os.path.dirname(settings_filename)

    filename, _ = QFileDialog.getSaveFileName(
        self,
        "Save Settings File",
        initial_dir,
        "settings (*.param)"
    )

    if filename:
        settings_filename = os.path.splitext(filename)[0] + '.param'

    return settings_filename.split('.')[0] + '.param'


def remove_ext(filepath):
    """Returns the file without extension from a filepath"""
    return os.path.splitext(filepath)[0]


def remove_file(filepath):
    """Returns the top directory from a filepath"""
    return os.path.split(filepath)[0]


def get_ext(filepath):
    """Returns the extension from a filepath"""
    return os.path.splitext(filepath)[1]


def remove_path(filepath):
    """Returns the name of the file from a filepath"""
    return os.path.split(filepath)[1]


def smart_number_sort(filenames):
    filename_sort = []

    for filename in filenames:
        filename_sort.append(''.join([i for i in filename if i in '0123456789']))

    len_filenames = [len(number) for number in filename_sort]
    sorted_filenames = [x for _, _, x in sorted(zip(len_filenames, filename_sort, filenames))]
    return sorted_filenames


def list_files(directory, reverse_sort=False, smart_sort=None, relative=False, extension=None):
    """
    Returns all the files from a directory.
    """
    if extension is not None:
        directory += '*' + extension
    files = glob.glob(directory)

    if smart_sort is None:
        files.sort(reverse=reverse_sort)
    else:
        files = smart_sort(files)

    if relative:
        return [remove_path(f) for f in files]
    return files


get_directory_filenames = list_files


def get_filenames(initialdir='/', title='Choose files', filetypes=None):
    _app = _ensure_app()
    filter_str = ";;".join([f"{label} ({pattern})" for label, pattern in filetypes]) if filetypes else ""
    files, _ = QFileDialog.getOpenFileNames(None, title, initialdir, filter_str)
    return files


class BatchProcess:
    """
    BatchProcess is a generator that enables you to easily iterate through a selection
    of files in a directory.
    """

    def __init__(self, directory, extension=None, relative=False, smart_sort=None, reverse_sort=False):
        self.files = get_directory_filenames(
            directory,
            reverse_sort=reverse_sort,
            relative=relative,
            smart_sort=smart_sort,
            extension=extension
        )
        self.num_files = len(self.files)
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            file = self.files[self.current]
            self.current += 1
        except IndexError:
            raise StopIteration
        return file


def datetime_stamp(format_string="%Y%m%d_%H%M%S"):
    now = time.gmtime()
    return time.strftime(format_string)