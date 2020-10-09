from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from os.path import isfile
from pathlib import Path
import cv2
import sys


from .gui.image_viewer import QtImageViewer
from .project.workflow import PTProject
from .gui.slidergroupwidgets_pyqt5 import Spinbox_Slider
from .gui.checked_tab_widget import CheckableTabWidget
from .general.writeread_param_dict import write_paramdict_file
from filehandling import BatchProcess

PACKAGE_DIR = os.path.dirname(__file__)
TESTDATA_DIR = PACKAGE_DIR+'/testdata/'
CONTOURS_VID = TESTDATA_DIR + 'contours.mp4'
CONTOURS_PARAM = TESTDATA_DIR + 'contours.param'
BOXES_VID = TESTDATA_DIR + 'boxes.mp4'
BOXES_PARAM = TESTDATA_DIR + 'boxes.param'
HOUGH_VID = TESTDATA_DIR + 'hough.mp4'
HOUGH_PARAM = TESTDATA_DIR + 'hough.param'
TRACKPY_VID = TESTDATA_DIR + 'trackpy.mp4'
TRACKPY_PARAM = TESTDATA_DIR + 'trackpy.param'
DEFAULT_PARAM = TESTDATA_DIR + 'default.param'

__all__ = ['CONTOURS_VID', 'CONTOURS_PARAM', 'HOUGH_PARAM', 'HOUGH_VID', 'TRACKPY_VID', 'TRACKPY_PARAM']


class MainWindow(QMainWindow):
    def __init__(self, *args, movie_filename=None, settings_filename=None, **kwargs):
        super(MainWindow,self).__init__(*args, **kwargs)
        EXIT_CODE_REBOOT = -123

        if movie_filename is None:
            self.movie_filename = None
        elif isfile(movie_filename):
            self.movie_filename = str(Path(movie_filename))
        else:
            self.movie_filename = None

        if settings_filename is None:
            self.settings_filename = None
        elif isfile(settings_filename):
            self.settings_filename = str(Path(settings_filename))
        else:
            self.settings_filename = None

        self.reboot()

    def reboot(self):
        if hasattr(self, 'main_panel'):
            self.main_panel.deleteLater()
            self.main_panel.setParent(None)
        self.open_tracker()
        self.setWindowTitle("Particle Tracker")

        self.main_panel = QWidget()
        self.main_layout = QHBoxLayout()  # Contains view and settings layout
        self.view_layout = QVBoxLayout()  # Contains image, image toggle button and frame slider
        self.settings_layout = QVBoxLayout()  # Contains tab widget with all tracking controls
        # Qt namespace has a lot of attributes for widgets: http://doc.qt.io/qt-5/qt.html
        self.init_ui(self.view_layout, self.settings_layout)
        self.main_layout.addLayout(self.view_layout)
        self.main_layout.addLayout(self.settings_layout)
        self.main_panel.setLayout(self.main_layout)
        self.setCentralWidget(self.main_panel)
        self.showMaximized()


    def init_ui(self, view_layout, settings_layout, reboot=True):
        if not hasattr(self, 'file_menu'):
            self.setup_menus_toolbar()

        self.setup_viewer(view_layout)# Contains image window, frame slider and spinbox.
        self.setup_settings_panel(settings_layout)
        # Contains all widgets on rhs.

    def setup_menus_toolbar(self):
        dir = os.path.abspath(__file__)
        resources_dir = os.path.join(dir[:-11],'gui','icons','icons')
        self.toolbar = QToolBar('Toolbar')
        self.toolbar.setIconSize(QSize(16,16))
        self.addToolBar(self.toolbar)
        open_movie_button = QAction(QIcon(os.path.join(resources_dir,"folder-open-film.png")), "Open File", self)
        open_movie_button.setStatusTip("Open Movie or Img Sequence")
        open_movie_button.triggered.connect(self.open_movie_click)
        self.toolbar.addAction(open_movie_button)

        open_settings_button = QAction(QIcon(os.path.join(resources_dir,"script-import.png")), "Open Settings File", self)
        open_settings_button.setStatusTip("Open Movie or Img Sequence")
        open_settings_button.triggered.connect(self.open_settings_button_click)
        self.toolbar.addAction(open_settings_button)

        save_settings_button = QAction(QIcon(os.path.join(resources_dir,"script-export.png")), "Save Settings File", self)
        save_settings_button.setStatusTip("Save Settings")
        save_settings_button.triggered.connect(self.save_settings_button_click)
        self.toolbar.addAction(save_settings_button)

        self.toolbar.addSeparator()

        self.live_update_button = QAction(QIcon(os.path.join(resources_dir,"arrow-circle.png")), "Live Updates", self)
        self.live_update_button.setCheckable(True)
        self.live_update_button.setChecked(True)
        self.live_update_button.triggered.connect(self.live_update_button_click)
        self.toolbar.addAction(self.live_update_button)

        self.toolbar.addSeparator()

        process_part_button = QAction(QIcon(os.path.join(resources_dir,"clapperboard--minus.png")), "Process part", self)
        process_part_button.triggered.connect(self.process_part_button_click)
        self.toolbar.addAction(process_part_button)

        self.use_part_button = QAction(QIcon(os.path.join(resources_dir,"fire--exclamation.png")), "Use part processed", self)
        self.use_part_button.setCheckable(True)
        self.use_part_button.setChecked(False)
        self.use_part_button.triggered.connect(self.use_part_button_click)
        self.toolbar.addAction(self.use_part_button)

        process_button = QAction(QIcon(os.path.join(resources_dir,"clapperboard--arrow.png")), "Process", self)
        process_button.triggered.connect(self.process_button_click)
        self.toolbar.addAction(process_button)

        self.toolbar.addSeparator()

        close_button = QAction(QIcon(os.path.join(resources_dir,"cross-button.png")), "Close", self)
        close_button.triggered.connect(self.close_button_click)
        self.toolbar.addAction(close_button)

        statusbar = QStatusBar(self)
        self.setStatusBar(statusbar)
        menu = self.menuBar()

        self.file_menu = menu.addMenu("&File")
        self.file_menu.addAction(open_movie_button)
        self.file_menu.addAction(open_settings_button)
        self.file_menu.addAction(save_settings_button)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.live_update_button)
        self.file_menu.addSeparator()
        self.file_menu.addAction(process_part_button)
        self.file_menu.addAction(self.use_part_button)
        self.file_menu.addAction(process_button)
        self.file_menu.addSeparator()
        self.file_menu.addAction(close_button)

    def setup_viewer(self, view_layout):
        self.viewer_is_setup = True
        self.movie_label = QLabel(self.movie_filename)
        self.settings_label = QLabel(self.settings_filename)
        self.viewer = QtImageViewer()
        self.toggle_img = QPushButton("Preprocessed Image")
        self.toggle_img.setCheckable(True)
        self.toggle_img.setChecked(False)
        self.toggle_img.clicked.connect(self.select_img_view)
        param_dict = {}
        param_dict['frame']={}
        param_dict['frame']['frame']=[self.tracker.cap.frame_range[0], self.tracker.cap.frame_range[0], self.tracker.cap.frame_range[1]-1, self.tracker.cap.frame_range[2]]
        self.frame_selector = Spinbox_Slider('frame','frame',param_dict,update_viewer_fn=self.update_viewer)
        self.update_viewer()
        view_layout.addWidget(self.movie_label)
        view_layout.addWidget(self.settings_label)
        view_layout.addWidget(self.viewer)
        view_layout.addWidget(self.toggle_img)
        view_layout.addWidget(self.frame_selector)

    def update_viewer(self):
        if self.live_update_button.isChecked():
            frame_number = self.frame_selector.param_list['frame']['frame'][0]
            try:
                #Check dictionary is updated.

                if self.use_part_button.isChecked():
                    annotated_img, proc_img = self.tracker.process_frame(frame_number, use_part=True)
                else:
                    annotated_img, proc_img = self.tracker.process_frame(frame_number)

                toggle = self.toggle_img.isChecked()
                if toggle:
                    self.viewer.setImage(self.bgr_to_rgb(proc_img))
                else:
                    self.viewer.setImage(self.bgr_to_rgb(annotated_img))
            except Exception as e:
                '''
                This is called to reverse a settings change that was made.
                Usually the user has asked for an impossible combination 
                of methods to be applied. See CheckableTabWidgets --> MyListWidget
                '''
                print(e)

                # self.toplevel_settings.deactivate_last_added_method()
                msgBox = QMessageBox.about(self, "Warning",
                                   "Tracking crashed: It is likely "
                                   "you asked for a incompatible set of methods / parameters."
                                   "Best suggestion undo whatever you just did!")


    def reset_viewer(self):
        param_dict = {}
        param_dict['frame'] = {}
        param_dict['frame']['frame'] = [self.tracker.cap.frame_range[0],
                                        self.tracker.cap.frame_range[0],
                                        self.tracker.cap.frame_range[1] - 1,
                                        self.tracker.cap.frame_range[2]]
        self.frame_selector.update_params(param_dict)
        self.movie_label.setText(self.movie_filename)

    def select_img_view(self):
        if self.toggle_img.isChecked():
            self.toggle_img.setText("Preprocessed Image")
        else:
            self.toggle_img.setText("Captured Image")
        self.update_viewer()

    def bgr_to_rgb(self, img):
        '''BGR or RGB that is the question. Opencv
        and PyQT have a different answer so convert
        the opencv images prior to sending to
        PyQT so that gui and exported things look
        the same.'''
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def setup_settings_panel(self, settings_layout):
        self.toplevel_settings = CheckableTabWidget(self.tracker, self.update_viewer, self.viewer, reboot=self.reboot)
        settings_layout.addWidget(self.toplevel_settings)

    """---------------------------------------------------------------         
    ------------------------------------------------------------------
    Callback functions
    ------------------------------------------------------------------
    ----------------------------------------------------------------"""
    def open_tracker(self):
        if self.movie_filename is None:
            ok = False
            while not ok:
                ok = self.open_movie_dialog()
        if self.settings_filename is None:
            self.open_settings_button_click()

        self.tracker = PTProject(video_filename=self.movie_filename, param_filename=self.settings_filename)
        if hasattr(self, 'viewer_is_setup'):
            self.reset_viewer()

    def open_movie_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.recovery_movie_filename = self.movie_filename
        if self.movie_filename is None:
            movie_filename, ok = QFileDialog.getOpenFileName(self, "Open Movie or Img Sequence", QDir.homePath(),
                                                            "mp4 (*.mp4);;avi (*.avi);;m4v (*.m4v)", options=options)
        else:
            movie_filename, ok = QFileDialog.getOpenFileName(self, "Open Movie or Img Sequence",
                                                            self.movie_filename.split('.')[0],
                                                            "mp4 (*.mp4);;avi (*.avi);;m4v (*.m4v)", options=options)
        if ok:
            self.movie_filename = movie_filename
            return True
        else:
            return False

    def open_movie_click(self):
        try:
            self.open_movie_dialog()
            self.reboot()
        except:
            self.movie_filename = self.recovery_movie_filename
            self.reboot()

    def open_settings_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.recovery_settings_filename = self.settings_filename
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


    def open_settings_button_click(self):
        try:
            self.open_settings_dialog()
            self.reboot()#Reboots the entire GUI
        except:
            self.settings_filename = self.recovery_settings_filename
            self.reboot()

    def save_settings_button_click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_settings_name, _ = QFileDialog.getSaveFileName(self, "Save Settings File", self.settings_filename.split('.')[0],
                                                        "settings (*.param)", options=options)

        num_tabs = len(self.toplevel_settings.list_draggable_lists)
        for i in range(num_tabs):
            draggable_list = self.toplevel_settings.list_draggable_lists[i]
            draggable_list.update_dictionary()

        file_settings_name=file_settings_name.split('.')[0] + '.param'
        write_paramdict_file(self.tracker.parameters, file_settings_name)

    def live_update_button_click(self):
        if self.live_update_button.isChecked():
            self.update_viewer()

    def process_part_button_click(self):
        '''
        This button processes the movie but it skips the postprocess and annotation steps
        It is designed as a first step to experiment with different postprocessing and
        and annotation steps. Some of these require data from other frames which is not
        possible if you just process a single frame. To then process that data you need
        to check the use_part_button.
        '''
        postprocess_init_state = self.tracker.postprocess_select
        annotate_init_state = self.tracker.postprocess_select
        self.tracker.postprocess_select = False
        self.tracker.annotate_select = False
        self.process_button_click()
        self.tracker.postprocess_select = postprocess_init_state
        self.tracker.annotate_select = annotate_init_state

    def use_part_button_click(self):
        '''This code only changes appearance of gui and checks
        to see if .hdf5 data file exists. The commands tracker.process
        and tracker.process_frame take a keyword use_part which
        is set by checking toggle status of this button.
        '''
        if isfile(self.movie_filename[:-4] + '.hdf5'):
            #Greys out / un greys the tabs which are not being used
            for i in range(5):
                if self.use_part_button.isChecked():
                    self.toplevel_settings.disable_tabs(i,enable=False)
                else:
                    self.toplevel_settings.disable_tabs(i, enable=True)
        else:
            self.use_part_button.setChecked(False)
            QMessageBox.about(self, "", "You must run 'Process Part' before you can use this")

    def process_button_click(self):
        self.tracker.reset_annotator()
        if self.use_part_button.isChecked():
            self.tracker.process(use_part=True)
        else:
            self.tracker.process()

        write_paramdict_file(self.tracker.parameters, self.movie_filename[:-4] + '_expt.param')
        QMessageBox.about(self, "", "Processing Finished")
        self.reboot()

    def close_button_click(self):
        sys.exit()




def track_gui(movie=None, settings=None):
    '''

    Parameters
    ----------
    movie: optional path to movie to process
    settings: optional path to .param settings config file

    Returns None
    -------

    '''
    app = QApplication(sys.argv)
    window = MainWindow(
        movie_filename=movie,
        settings_filename=settings)
    window.show()
    #Start event loop
    app.exec_()





def track_batchprocess(moviefilter, settings, crop=True, preprocess=True, track=True, link=True, postprocess=True,
                 annotate=True):
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
        track = PTProject(video_filename=filename, param_filename=settings)
        track.crop_select = crop
        track.preprocess_select = preprocess
        track.track_select = track
        track.link_select = link
        track.postprocess_select = postprocess
        track.annotate_select = annotate
        track.process()


