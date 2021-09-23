from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from os.path import isfile
from pathlib import Path
import cv2
import sys
import numpy as np
import qimage2ndarray
import webbrowser
import shutil
import time

from qtwidgets.sliders import QCustomSlider
from qtwidgets.images import QImageViewer


from .custom_tab_widget import CheckableTabWidget
from ..project import PTWorkflow
from ..general.writeread_param_dict import write_paramdict_file
from ..general.parameters import parse_values
from ..general.param_file_creator import create_param_file
from ..general.imageformat import bgr_to_rgb

from .. import project

from .pandas_view import PandasWidget

class MainWindow(QMainWindow):
    
    def __init__(self, *args, movie_filename=None, settings_filename=None, **kwargs):
        super(MainWindow,self).__init__(*args, **kwargs)
        
        self.movie_filename=None
        if movie_filename is not None:
            if isfile(movie_filename):
                self.movie_filename = str(Path(movie_filename))
            else:
                movie_filename = None
            
        if movie_filename is None:
            ok, self.movie_filename = self.open_movie_dialog()

        if settings_filename is not None:
            if isfile(settings_filename):
                self.settings_filename = str(Path(settings_filename))
            else:
                settings_filename = None
        
        if settings_filename is None:
            self.load_default_settings()    

        self.reboot()


    def reboot(self, open_settings=True):
        
        if hasattr(self, 'main_panel'):
            self.main_panel.deleteLater()
            self.main_panel.setParent(None)
            if not open_settings:
                try:
                    #This allows for continuity of parameters after processing.
                    self.settings_filename = self.movie_filename[:-4] + '_expt.param'
                except:
                    print('tried to load current params - falling back on initial settings file')
        
        self.open_tracker()
        self.setup_pandas_viewer()
        self.setWindowTitle("Particle Tracker")

        self.main_panel = QWidget()
        self.main_layout = QHBoxLayout()  # Contains view and settings layout
        self.view_layout = QVBoxLayout()  # Contains image, image toggle button and frame slider
        self.settings_layout = QVBoxLayout()  # Contains tab widget with all tracking controls

        self.init_ui()#self.view_layout, self.settings_layout)
        
        self.main_layout.addLayout(self.view_layout,3)
        self.main_layout.addLayout(self.settings_layout,2)
        self.main_panel.setLayout(self.main_layout)
        self.setCentralWidget(self.main_panel)
        self.showFullScreen()
        self.showMaximized()
        

    def init_ui(self):#, view_layout, settings_layout, reboot=True):
        if not hasattr(self, 'file_menu'):
            self.setup_menus_toolbar()
        else:
            #This solves a bug which occurs when you have use_part_button checked
            #and open a new video which has no .hdf5 file.
            self.use_part_button.setChecked(False)

        self.setup_viewer(self.view_layout)# Contains image window, frame slider and spinbox.
        self.setup_settings_panel(self.settings_layout)# Contains all widgets on rhs of gui.
      

        """------------------------------------------------------------------------------
        ------------------------------------------------------------------------------
        SETUP MENUS AND TOOLBAR
        
        Setup of all the menus and toolbars at the bottom. The statusbar at the bottom
        is also initialised here.
        ---------------------------------------------------------------------------------
        ---------------------------------------------------------------------------------"""

    def setup_menus_toolbar(self):
        dir,_ =os.path.split(os.path.abspath(__file__))
        resources_dir = os.path.join(dir,'icons','icons')
        #Use these lines when using pyinstaller.
        #dir , _= os.path.split(sys.argv[0])#os.path.abspath(__file__)
        #resources_dir = os.path.join(dir,'gui','icons','icons')
        self.toolbar = QToolBar('Toolbar')
        self.toolbar.setIconSize(QSize(16,16))
        self.addToolBar(self.toolbar)

        '''
        ---------------------------------------------------------------------------------------------------
        Buttons on toolbar
        ---------------------------------------------------------------------------------------------------
        '''
        open_movie_button = QAction(QIcon(os.path.join(resources_dir,"folder-open-film.png")), "Open File", self)
        open_movie_button.setStatusTip("Open Movie")
        open_movie_button.triggered.connect(self.open_movie_click)
        self.toolbar.addAction(open_movie_button)

        open_settings_button = QAction(QIcon(os.path.join(resources_dir,"script-import.png")), "Open Settings File", self)
        open_settings_button.setStatusTip("Open Movie")
        open_settings_button.triggered.connect(self.open_settings_button_click)
        self.toolbar.addAction(open_settings_button)

        save_settings_button = QAction(QIcon(os.path.join(resources_dir,"script-export.png")), "Save Settings File", self)
        save_settings_button.setStatusTip("Save Settings")
        save_settings_button.triggered.connect(self.save_settings_button_click)
        self.toolbar.addAction(save_settings_button)

        self.autosave_on_process = QAction(QIcon(os.path.join(resources_dir,"autosave.png")), 'Autosave settings on process', self)
        self.autosave_on_process.setCheckable(True)
        self.autosave_on_process.setChecked(True)
        self.toolbar.addAction(self.autosave_on_process)

        self.toolbar.addSeparator()

        self.live_update_button = QAction(QIcon(os.path.join(resources_dir,"arrow-circle.png")), "Live Updates", self)
        self.live_update_button.setCheckable(True)
        self.live_update_button.setChecked(True)
        self.live_update_button.triggered.connect(self.live_update_button_click)
        self.toolbar.addAction(self.live_update_button)

        self.toolbar.addSeparator()

        pandas_button = QAction(
            QIcon(os.path.join(resources_dir, "view_pandas.png")),
            "Show Dataframe View", self)
        pandas_button.triggered.connect(self.pandas_button_click)
        self.toolbar.addAction(pandas_button)

        self.csv=False
        self.export_to_csv = QAction(QIcon(os.path.join(resources_dir,"excel.png")),'Export to csv', self)
        self.export_to_csv.triggered.connect(self.export_to_csv_click)
        self.export_to_csv.setCheckable(True)
        self.toolbar.addAction(self.export_to_csv)

        process_part_button = QAction(QIcon(os.path.join(resources_dir,"clapperboard--minus.png")), "Process part", self)
        process_part_button.triggered.connect(self.process_part_button_click)
        self.toolbar.addAction(process_part_button)

        self.use_part_button = QAction(QIcon(os.path.join(resources_dir,"fire--exclamation.png")), "Use part processed", self)
        self.use_part_button.setCheckable(True)
        self.use_part_button.triggered.connect(self.use_part_button_click)
        self.toolbar.addAction(self.use_part_button)

        process_button = QAction(QIcon(os.path.join(resources_dir,"clapperboard--arrow.png")), "Process", self)
        process_button.triggered.connect(self.process_button_click)
        self.toolbar.addAction(process_button)

        self.toolbar.addSeparator()

        close_button = QAction(QIcon(os.path.join(resources_dir,"cross-button.png")), "Close", self)
        close_button.triggered.connect(self.close_button_click)
        self.toolbar.addAction(close_button)



        menu = self.menuBar()

        self.status_bar = QStatusBar(self)
        font = QFont()
        font.setPointSize(14)
        self.status_bar.setFont(font)
        self.setStatusBar(self.status_bar)
        

        '''
        ---------------------------------------------------------------------------------------------
        File menu items
        ---------------------------------------------------------------------------------------------
        '''
        self.file_menu = menu.addMenu("&File")
        self.process_menu = menu.addMenu("Process options")
        self.help_menu = menu.addMenu("Help")

        load_defaults = QAction('Load default settings', self)
        load_defaults.triggered.connect(self.load_default_settings)

        self.file_menu.addAction(open_movie_button)
        self.file_menu.addAction(open_settings_button)
        self.file_menu.addAction(save_settings_button)
        self.file_menu.addAction(load_defaults)
        self.file_menu.addSeparator()
        self.file_menu.addAction(close_button)

        self.process_menu.addAction(self.autosave_on_process)
        self.process_menu.addAction(self.export_to_csv)
        self.process_menu.addAction(process_part_button)
        self.process_menu.addAction(self.use_part_button)
        self.process_menu.addAction(process_button)
        
        docs = QAction('help', self)
        docs.triggered.connect(self.open_docs)
        about = QAction('about', self)
        about.triggered.connect(self.about)

        self.help_menu.addAction(docs)
        self.help_menu.addAction(about)

       
    def open_docs(self):
        webbrowser.open('https://particle-tracker.readthedocs.io/en/latest/', new=1, autoraise=True)
    
    def about(self):
        msg=QMessageBox(self)
        msg.setText(
            """Particle tracker was created by Mike Smith and James Downs. 
            Its purpose is to provide a simple platform for quickly performing 
            both simple and complicated tracking of objects in images / movies.
            The software is provided free of charge and can be used as you see fit.
            If used academically we would ask that you cite our page. 
            We are happy to consider feature requests."""
            )
        msg.show()



        """-----------------------------------------------------------------------------------------------
        --------------------------------------------------------------------------------------------------
        SETUP VIEWER
        
        Setup for the viewer panel - LHS of Gui includes viewer, frame selector and capture v preprocessing
        image toggle button.
        --------------------------------------------------------------------------------------------------
        ----------------------------------------------------------------------------------------------"""

    def setup_viewer(self, view_layout):
        '''
        Viewer is the LHS of gui containing window, frame_slider etc
        '''
        self.viewer_is_setup = True
        self.movie_label = QLabel(self.movie_filename)
        self.settings_label = QLabel(self.settings_filename)
        self.viewer = QImageViewer()
        self.viewer.leftMouseButtonDoubleClicked.connect(self.coords_clicked)
        self.toggle_img = QPushButton("Captured Image")
        self.toggle_img.setCheckable(True)
        self.toggle_img.clicked.connect(self.select_img_view)
        self.toggle_img.setChecked(False)
        
        frame_selector_layout = QHBoxLayout()

        if self.tracker.parameters['experiment']['frame_range'][1] is None:
            max_val = self.tracker.cap.num_frames - 1
        else:
            max_val=self.tracker.parameters['experiment']['frame_range'][1] - 1
        self.frame_selector = QCustomSlider(title='Frame',
                                            min_=self.tracker.parameters['experiment']['frame_range'][0],
                                            max_=max_val,
                                            step_=self.tracker.parameters['experiment']['frame_range'][2],
                                            value_=self.tracker.cap.frame_range[0],
                                            spinbox=True,
                                            )
        self.frame_selector.meta = ['experiment','frame']
        self.frame_selector.valueChanged.connect(lambda x=self.frame_selector.value():self.param_change(x))
        self.frame_selector.rangeChanged.connect(lambda x: self.param_change(x))
        self.frame_selector.widget = 'slider'
        self.reset_frame_range = QPushButton('Reset frame range')
        self.reset_frame_range.clicked.connect(self.reset_frame_range_click)
        self.reset_frame_range.meta = 'ResetFrameRange'

        view_layout.addWidget(self.movie_label)
        view_layout.addWidget(self.settings_label)
        view_layout.addWidget(self.viewer)
        view_layout.addWidget(self.toggle_img)
        frame_selector_layout.addWidget(self.frame_selector)
        frame_selector_layout.addWidget(self.reset_frame_range)
        view_layout.addLayout(frame_selector_layout)
        
        self.update_viewer()
        

    '''---------------------------------------------------------------
    -------------------------------------------------------------------
    SETUP SETTINGS PANEL

    Settings panel is the rhs of gui containing all the param adjustors
    -------------------------------------------------------------------
    --------------------------------------------------------------------
    '''
    def setup_settings_panel(self, settings_layout):
        self.toplevel_settings = CheckableTabWidget(self.tracker, self.viewer, self.param_change, self.method_change, reboot=self.reboot, parent=self)
        self.toplevel_settings.checkBoxChanged.connect(self.frame_selector_slot)
        settings_layout.addWidget(self.toplevel_settings)


    """
    ---------------------------------------------------------------         
    ------------------------------------------------------------------
    Callback functions
    ------------------------------------------------------------------
    ----------------------------------------------------------------
    """
    def open_tracker(self):
        """PTWorkFlow is the top level class that controls the entire tracking process
        """
        self.tracker = PTWorkflow(video_filename=self.movie_filename, param_filename=self.settings_filename, error_reporting=self)
        if hasattr(self, 'viewer_is_setup'):
            self.reset_viewer()



    @pyqtSlot(float, float)
    def coords_clicked(self, x, y):
        """This slot is linked to a left mouse click in the viewer
        x and y are the coordinates of the click. The coords and rgb 
        values are displayed in the status bar temporarily and outputted
        to the command window.

        """
        print('Coords')
        print(x, y)
        print('Intensities [r,g,b]')
        Qimg = self.viewer.image()
        output = qimage2ndarray.rgb_view(Qimg)
        print(output[int(y),int(x),:])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.reset_statusbar)
        self.timer.start(8000)
        self.status_bar.setStyleSheet("background-color : green")
        self.status_bar.showMessage("Coords (x,y): ("+str(x)+','+str(y) +') \t Intensities [r,g,b]:'+str(output[int(y),int(x),:]))    
        self.show()
  

    def reset_statusbar(self):
        self.status_bar.setStyleSheet("background-color : lightGray")
        self.status_bar.clearMessage()
        
    @pyqtSlot(int)
    def frame_selector_slot(self, value):
        self.update_viewer()

    @pyqtSlot()
    def param_change(self, value):
        """
        This slot is linked to by a wide variety of signals from the rhs of the gui
        Whenever a parameter is changed via a slider etc a signal is sent to this slot
        which contains the new value. the signal has meta data associated with it 
        which tells us where the signal has come from and hence what needs to be done with the value

        The values are sent to update the dictionary of settings and the viewer is reloaded with the image
        processed with the new settings.

        """
        sender = self.sender()
        paramdict_location=sender.meta
        
        if sender.meta == 'ResetFrameRange':
            self.update_dictionary_params(['experiment','frame_range'],(0,self.tracker.cap.num_frames-1,1), 'button')
            self.tracker.cap.set_frame_range((0,self.tracker.cap.num_frames,1))
        elif ('frame' in paramdict_location[1]) and (type(value) == tuple):
            frame_range = (self.frame_selector.slider._min,self.frame_selector.slider._max+1,self.frame_selector.slider._step)
            if (frame_range[1] <= self.tracker.cap.num_frames) | (frame_range[1] is None):
                self.update_dictionary_params(['experiment','frame_range'],frame_range, 'slider')
                self.tracker.cap.set_frame_range(frame_range)
            else:
                self.reset_frame_range_click()
        elif sender.meta == 'ResetMask':
            self.tracker.cap.reset()
            self.update_param_widgets('crop')
            self.viewer.clearImage()
        else:
            parsed_value = parse_values(sender, value)
            self.update_dictionary_params(paramdict_location, parsed_value, sender.widget)
            if ('crop' in paramdict_location[1]):
                self.tracker.cap.reset_mask()
                self.update_dictionary_params(['crop','mask_rectangle'], None, 'textbox')
                self.update_dictionary_params(['crop','mask_circle'], None, 'textbox')
                self.update_dictionary_params(['crop','mask_ellipse'], None, 'textbox')
                self.update_dictionary_params(['crop','mask_polygon'], None, 'textbox')
                self.update_param_widgets('crop')
            if ('crop' in paramdict_location[1]) or ('mask' in paramdict_location[1]):
                self.tracker.cap.set_mask()          
        
        self.update_viewer()
        self.update_pandas_view()


    @pyqtSlot(tuple)
    def method_change(self, value):
        """
        This slot is linked to a change in the methods (top rhs of gui). 
        MyListWidget in custom_drag_drop_list has the signal but we also trigger
        that signal in custom_combo_box.py in omboBoxAndButton.add_method_button_click()
        """
        sender = self.sender()
        location = [sender.title, sender.title + '_method']
        self.update_dictionary_params(location, value, 'list')
        self.update_param_widgets(sender.title)
        self.update_viewer()


        """------------------------------------------------------
        Various methods to update sections of the program.
        -------------------------------------------------------"""

    def update_dictionary_params(self, location, value, widget_type):
        if len(location) == 2:
            '''Sometimes a duplicate method is added to method list which is not
            in the dictionary. These duplicates are named method*1 etc. There will
            already be a method in the dictionary. We copy these values to the
            newly created method.
            '''
            if '_method' in location[1]:
                if value == ():
                    self.tracker.parameters[location[0]][location[1]] = value
                else:
                    for item in value:
                        if item in self.tracker.parameters[location[0]].keys():
                            self.tracker.parameters[location[0]][location[1]] = value
                        else:
                            assert '*' in item, "Key not in dict and doesn't contain *"
                            if type(self.tracker.parameters[location[0]][item.split('*')[0]]) is dict:
                                    self.tracker.parameters[location[0]][item] = self.tracker.parameters[location[0]][item.split('*')[0]].copy()
                            else:
                                self.tracker.parameters[location[0]][item] = self.tracker.parameters[location[0]][item.split('*')[0]]
            else:
                if widget_type == 'dropdown':
                    self.tracker.parameters[location[0]][location[1]][0] = value
                else:
                    self.tracker.parameters[location[0]][location[1]] = value
        else:
            if widget_type == 'dropdown':
                self.tracker.parameters[location[0]][location[1]][location[2]][0] = value 
            else:
                self.tracker.parameters[location[0]][location[1]][location[2]] = value 

    def update_param_widgets(self, title):
        for param_adjustor in self.toplevel_settings.list_param_adjustors:
            if param_adjustor.title == title:  
                param_adjustor.remove_widgets()
                param_adjustor.build_widgets(title, self.tracker.parameters[title])

    def update_viewer(self):
        if self.live_update_button.isChecked():
            frame_number = self.frame_selector.value()
            if self.use_part_button.isChecked():
                annotated_img, proc_img = self.tracker.process_frame(frame_number, use_part=True)
            else:
                annotated_img, proc_img = self.tracker.process_frame(frame_number)

            toggle = self.toggle_img.isChecked()
            if toggle:
                self.viewer.setImage(bgr_to_rgb(proc_img))
            else:
                self.viewer.setImage(bgr_to_rgb(annotated_img))
        
    def reset_viewer(self):
        self.frame_selector.changeSettings(min_=self.tracker.cap.frame_range[0],
                                           max_=self.tracker.cap.frame_range[1] - 1,
                                           step_=1,
                                           )
        self.movie_label.setText(self.movie_filename)

    def reset_frame_range_click(self):
        self.tracker.cap.set_frame_range((0,None,1))
        self.reset_viewer()    

    def select_img_view(self):
        if self.live_update_button.isChecked():
            if self.toggle_img.isChecked():
                self.toggle_img.setText("Preprocessed Image")
            else:
                self.toggle_img.setText("Captured Image")
            self.update_viewer()
    

        """-----------------------------------------------------------------
        File input and output
        -------------------------------------------------------------------"""

    def open_movie_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        if self.movie_filename is None:
            movie_filename, ok = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath(),
                                                            "mp4 (*.mp4);;avi (*.avi);;m4v (*.m4v)", options=options)
        else:
            movie_filename, ok = QFileDialog.getOpenFileName(self, "Open Movie",
                                                            self.movie_filename.split('.')[0],
                                                            "mp4 (*.mp4);;avi (*.avi);;m4v (*.m4v)", options=options)
 
        if ok:
            self.movie_filename = movie_filename
            return True, movie_filename
        else:
            return False, movie_filename

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

    def load_default_settings(self):
        pathname, _ = os.path.split(self.movie_filename)
        self.settings_filename = os.path.normpath(os.path.join(pathname, 'default.param'))
        create_param_file(self.settings_filename)
        self.reboot()

    def open_movie_click(self):
        ok, self.movie_filename=self.open_movie_dialog()
        if ok:
            self.reboot()
        
    def open_settings_button_click(self):
        ok=self.open_settings_dialog()
        if ok:
            self.reboot()
        
    def save_settings_button_click(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        file_settings_name, _ = QFileDialog.getSaveFileName(self, "Save Settings File", self.settings_filename.split('.')[0],
                                                        "settings (*.param)", options=options)

        file_settings_name=file_settings_name.split('.')[0] + '.param'
        write_paramdict_file(self.tracker.parameters, file_settings_name)

    def export_to_csv_click(self):
        self.csv = self.export_to_csv.isChecked


        """------------------------------------------------------------
        Functions that control the processing
        --------------------------------------------------------------"""
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
            for i in range(5):#index cycles through different tabs from experiment to link
                if self.use_part_button.isChecked():
                    self.toplevel_settings.disable_tabs(i,enable=False)
                    self.toggle_img.setChecked(False)
                    self.select_img_view()
                    self.toggle_img.setCheckable(False)
                else:
                    self.toplevel_settings.disable_tabs(i, enable=True)
                    self.toggle_img.setCheckable(True)
        else:
            self.use_part_button.setChecked(False)
            QMessageBox.about(self, "", "You must run 'Process Part' before you can use this")

    def process_button_click(self): 
        self.status_bar.setStyleSheet("background-color : lightBlue")
        self.status_bar.showMessage("Depending on the size of your movie etc this could take awhile. You can track progress in the command window.")    
        self.show()

        self.tracker.reset_annotator()
        if self.autosave_on_process.isChecked():
            write_paramdict_file(self.tracker.parameters, self.settings_filename)

        if self.use_part_button.isChecked():
            self.tracker.process(use_part=True, csv=self.csv)
        else:
            self.tracker.process(csv=self.csv)

        write_paramdict_file(self.tracker.parameters, self.movie_filename[:-4] + '_expt.param')
        
        self.reset_statusbar()
        QMessageBox.about(self, "", "Processing Finished")
        self.reboot(open_settings=False)

    def close_button_click(self):
        sys.exit()

    def setup_pandas_viewer(self):
        self.pandas_viewer = PandasWidget(self)
        fname = self.tracker.data_filename
        fname = fname[:-5] + '_temp.hdf5'
        self.pandas_viewer.update_file(fname)

    def pandas_button_click(self):
        self.pandas_viewer.show()

    def update_pandas_view(self):
        fname = self.tracker.data_filename
        if not self.use_part_button.isChecked():
            fname = fname[:-5]+'_temp.hdf5'
        self.pandas_viewer.update_file(fname)

