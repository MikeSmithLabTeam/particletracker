import os
import glob
import time
from PyQt6.QtWidgets import QFileDialog, QApplication


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



def create_directory(
        initialdir='/',
        title="Create directory",
        parent=None
):
    """
    Opens a directory selection dialog and returns the selected path.

    Parameters
    ----------
    initialdir : str
        The initial directory

    title : str
        Message box title

    parent : widget
        Optional Qt parent widget.

    Returns
    -------
    directory : str
        The selected directory path, or an empty string if cancelled.
    """
    _app = _ensure_app()
    directory = QFileDialog.getExistingDirectory(
        parent,
        title,
        initialdir,
        QFileDialog.Option.ShowDirsOnly)
    return directory


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
        filename_sort=[]

        #Secondary sort criterion is the numerical value
        for filename in filenames:
            filename_sort.append(''.join([i for i in filename if i in ['0','1','2','3','4','5','6','7','8','9']]))
        
        #Sort by length of number first. This means 01 goes before 001.
        len_filenames = [len(number) for number in filename_sort]

        sorted_filenames = [x for _,_,x in sorted(zip(len_filenames, filename_sort,filenames))] 
               
        return sorted_filenames


def list_files(directory, reverse_sort=False, smart_sort=None, relative=False,
                            extension=None):
    """
    Returns all the files from a directory.

    Can set the filetype using extension.

    Parameters
    ----------
    directory : str
        Filepath pointing to the directory with the final /
        Can use this with glob wildcards to use more complicated patterns.

    reverse_sort : bool
        If true files returns in reverse alphabetical order

    relative : bool
        If True files will be returned without the directory

    smart_sort : function_handle or None

    extension : str
        Extension filetype to be used as filter.

    Returns
    -------
    files : list
        List of all the files that match the pattern.

    """
    if extension is not None:
        directory += '*'+extension
    files = glob.glob(directory)

    if smart_sort is None:
        files.sort(reverse=reverse_sort)
    else:
        files = smart_sort(files)
    
    if relative:
        return [remove_path(f) for f in files]
    else:
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
    of files in a directoy.

    Attributes
    ----------
    num_files : int     The number of files in the selection
    current : int       The index of the file currently pointed at
    files : list        A list of strings of the filenames to be iterated over

    Returns
    -------
    file : str          A filename

    Examples
    --------
    directory is a path to a folder or expression for pattern matching.
    eg. /Documents/Example/a*b?.txt
    This returns files beginning in a with a b as the penultimate letter and file extension .txt

    for filename in BatchProcess(directory):
        print(filename)

    """

    def __init__(self, directory, extension=None, relative=False, smart_sort=None, reverse_sort=False):
        self.files = get_directory_filenames(
            directory,
            reverse_sort=reverse_sort,
            relative=relative,
            smart_sort=smart_sort,
            extension=extension)
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

def datetime_stamp(format_string = "%Y%m%d_%H%M%S"):
    """
    Get string for current date and time
    """
    now=time.gmtime()
    return time.strftime(format_string)
