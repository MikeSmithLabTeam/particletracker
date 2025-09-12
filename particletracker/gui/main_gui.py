#Packages
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QMessageBox,
    QStatusBar, QMenuBar, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QSize
from PyQt6.QtGui import QIcon, QFont, QAction

import os
from os.path import isfile
from pathlib import Path
import sys
import subprocess
import shutil
import qimage2ndarray
import webbrowser
from scipy import spatial
import copy

#Our other repos
from qtwidgets.sliders import QCustomSlider
from qtwidgets.images import QImageViewer
from labvision.images import write_img
from .menubar import CustomButton, CustomToolBar

#This project
from .custom_tab_widget import CustomTabWidget
from ..project import PTWorkflow
from ..general.writeread_param_dict import write_paramdict_file
from ..general.parameters import parse_values
from ..general.param_file_creator import create_param_file
from ..customexceptions import flash_error_msg

from ..general.imageformat import bgr_to_rgb
from .pandas_view import PandasWidget

from .file_io import check_filenames, open_movie_dialog, open_settings_dialog, save_settings_dialog




class MainWindow(QMainWindow):
    
    def __init__(self, *args, movie_filename=None, settings_filename=None, screen_size=None, **kwargs):
        super(MainWindow,self).__init__(*args, **kwargs)
        self.screen_size = screen_size
        # Calculate window size to leave room for status bar
        self.target_width = int(self.screen_size.width()) 
        self.target_height = int(self.screen_size.height() * 0.91) 
        self.setMinimumSize(800, 600)
        self.resize(self.target_width, self.target_height)
        
        
        self.movie_filename, self.settings_filename = check_filenames(self, movie_filename, settings_filename)
        if 'default.param' in self.settings_filename:
            create_param_file(self.settings_filename)
        self.reboot()

    def reboot(self):
        """The reboot method is used to reload the gui when opening a new video or settings file."""
        # Clean up existing GUI elements
        if hasattr(self, 'main_panel'):
            # Clear and remove toolbar
            if hasattr(self, 'toolbar'):
                self.removeToolBar(self.toolbar)
                self.toolbar.deleteLater()
            
            # Clear and remove menu bar
            if hasattr(self, 'menuBar'):
                menuBar = self.menuBar()
                menuBar.clear()
                menuBar.deleteLater()
                self.setMenuBar(QMenuBar(self))
                
            # Clean up main panel and its layouts
            self.main_layout.removeWidget(self.main_panel)
            self.main_panel.deleteLater()
            self.main_panel = None
            
            # Clean up status bar
            if hasattr(self, 'status_bar'):
                self.setStatusBar(None)
                self.status_bar.deleteLater()

      
        #Create the key behind the scenes object
        self.open_tracker()
        
        #Basic structural organising elements
        self.setWindowTitle("Particle Tracker")
        self.main_panel = QWidget()
        self.main_layout = QHBoxLayout()  # Contains view and settings layout
        self.view_layout = QVBoxLayout()  # Contains image, image toggle button and frame slider
        self.settings_layout = QVBoxLayout()  # Contains tab widget with all tracking controls

        #Create the gui
        self.setup_menus_toolbar()
        self.setup_viewer(self.view_layout)# Contains image window, frame slider and spinbox.
        self.setup_settings_panel(self.settings_layout)# Contains all widgets on rhs of gui.
        self.setup_pandas_viewer()
        self.setup_edit_pandas_viewer()

        #Add filled components to the main layout
        self.main_layout.addLayout(self.view_layout,3)
        self.main_layout.addLayout(self.settings_layout,2)
        self.main_panel.setLayout(self.main_layout)
        self.setCentralWidget(self.main_panel)
        
        # Center the window on screen
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

        #Set the lock state
        self.just_track_button.update_lock_buttons(self.tracker.parameters['config']['_locked_part'], checked=False)
        
        # Show window but don't maximize
        self.show()
        adjust_y = int((self.target_height-self.screen_size.height())/10)
        self.move(0, int((self.target_height-self.screen_size.height())/10)) # This will set the position
           
    def setup_menus_toolbar(self):
        dir,_ =os.path.split(os.path.abspath(__file__))
        resources_dir = os.path.join(dir,'icons','icons')
        self.toolbar = CustomToolBar('Toolbar')
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

        self.toolbar.addSeparator()
        spacer = QWidget()
        spacer.setFixedWidth(20)  # Set desired width in pixels
        self.toolbar.addWidget(spacer)
        self.toolbar.addSeparator()

        self.live_update_button = QAction(QIcon(os.path.join(resources_dir,"arrow-circle.png")), "Live Updates", self)
        self.live_update_button.setCheckable(True)
        self.live_update_button.setChecked(self.tracker.parameters['config']['_live_updates'])
        self.live_update_button.triggered.connect(self.live_update_button_click)
        self.toolbar.addAction(self.live_update_button)


        self.pandas_button = QAction(
            QIcon(os.path.join(resources_dir, "view_pandas.png")),
            "Show Dataframe View", self)
        self.pandas_button.triggered.connect(self.pandas_button_click)
        self.pandas_button.setCheckable(True)
        self.pandas_button.setChecked(False)
        self.toolbar.addAction(self.pandas_button)

        self.edit_pandas_button = QAction(
            QIcon(os.path.join(resources_dir, "edit_pandas.png")),
            "Show Dataframe View", self)
        self.edit_pandas_button.triggered.connect(self.edit_pandas_button_click)
        self.edit_pandas_button.setCheckable(True)
        self.edit_pandas_button.setChecked(False)
        self.toolbar.addAction(self.edit_pandas_button)

        self.snapshot_button = QAction(
            QIcon(os.path.join(resources_dir, "camera.png")),
            "Take snapshot", self)
        self.snapshot_button.triggered.connect(self.snapshot_button_click)
        self.toolbar.addAction(self.snapshot_button)

        self.cleanup = QAction(QIcon(os.path.join(resources_dir,"cleanup.png")), "Auto Cleanup", self)
        self.toolbar.addAction(self.cleanup)
        self.cleanup.triggered.connect(self.clean_up)

        self.toolbar.addSeparator()
        spacer = QWidget()
        spacer.setFixedWidth(20)  # Set desired width in pixels
        self.toolbar.addWidget(spacer)
        self.toolbar.addSeparator()        

        self.just_track_button = CustomButton(resources_dir, "track.png", vid_filename=self.movie_filename, part=0)
        self.toolbar.addWidget(self.just_track_button)
        self.just_track_button.lockButtons.connect(self.update_lock)

        self.just_link_button = CustomButton(resources_dir, "link.png",  vid_filename=self.movie_filename, part=1)
        self.toolbar.addWidget(self.just_link_button)
        self.just_link_button.lockButtons.connect(self.update_lock)

        self.just_postprocess_button = CustomButton(resources_dir, "postprocess.png",  vid_filename=self.movie_filename, part=2)
        self.toolbar.addWidget(self.just_postprocess_button)
        self.just_postprocess_button.lockButtons.connect(self.update_lock)
        
        self.toolbar.addSeparator()
        spacer = QWidget()
        spacer.setFixedWidth(20)  # Set desired width in pixels
        self.toolbar.addWidget(spacer)
        self.toolbar.addSeparator()

        process_button = QAction(QIcon(os.path.join(resources_dir,"clapperboard--arrow.png")), "Process", self)
        process_button.triggered.connect(self.process_button_click)
        self.toolbar.addAction(process_button)

        self.toolbar.addSeparator()
        spacer = QWidget()
        spacer.setFixedWidth(20)  # Set desired width in pixels
        self.toolbar.addWidget(spacer)
        self.toolbar.addSeparator()

        close_button = QAction(QIcon(os.path.join(resources_dir,"cross-button.png")), "Close", self)
        close_button.triggered.connect(self.close_button_click)
        self.toolbar.addAction(close_button)

        menu = self.menuBar()
        menu.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)  # Prevent context menu
        self.toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)  # Prevent 

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
        self.tool_menu = menu.addMenu("Tools")
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

        self.tool_menu.addAction(self.live_update_button)
        self.tool_menu.addAction(self.pandas_button)
        self.tool_menu.addAction(self.edit_pandas_button)
        self.tool_menu.addAction(self.snapshot_button)

        self.process_menu.addAction(self.cleanup)     
        self.process_menu.addAction(process_button)

        docs = QAction('help', self)
        docs.triggered.connect(self.open_docs)
        about = QAction('about', self)
        about.triggered.connect(self.about)

        self.help_menu.addAction(docs)
        self.help_menu.addAction(about)

    def load_default_settings(self):
        pathname, _ = os.path.split(self.movie_filename)
        self.settings_filename = os.path.normpath(os.path.join(pathname, 'default.param'))
        create_param_file(self.settings_filename)
        self.reboot()
       
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
        self.movie_label = QLabel('Current Video :  ' + self.movie_filename)
        self.settings_label = QLabel('Current Settings :  ' + self.settings_filename)
        self.viewer = QImageViewer()
        self.viewer.leftMouseButtonDoubleClicked.connect(self.coords_clicked)
        self.toggle_img = QPushButton("Captured Image")
        self.toggle_img.setCheckable(True)
        self.toggle_img.clicked.connect(self.select_img_view)
        self.toggle_img.setChecked(False)
        
        frame_selector_layout = QHBoxLayout()

        if self.tracker.parameters['config']['_frame_range'][1] is None:
            max_val = self.tracker.cap.num_frames - 1
        else:
            max_val=self.tracker.parameters['config']['_frame_range'][1] - 1
        self.frame_selector = QCustomSlider(title='Frame',
                                            min_=self.tracker.parameters['config']['_frame_range'][0],
                                            max_=max_val,
                                            step_=self.tracker.parameters['config']['_frame_range'][2],
                                            value_=self.tracker.cap.frame_range[0],
                                            spinbox=True,
                                            )
        self.frame_selector.meta = ['config','frame']
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
        self.toplevel_settings = CustomTabWidget(self.tracker, self.viewer, self.param_change, self.method_change, reboot=self.reboot)
        settings_layout.addWidget(self.toplevel_settings)

        #Connect up the locking of buttons to the deactivation / activation of panels
        self.just_track_button.lockButtons.connect(self.toplevel_settings.update_lock_state)
        self.just_link_button.lockButtons.connect(self.toplevel_settings.update_lock_state)
        self.just_postprocess_button.lockButtons.connect(self.toplevel_settings.update_lock_state)
        

    """
    ---------------------------------------------------------------         
    ------------------------------------------------------------------
    Callback functions
    ----------------------------------b--------------------------------
    ----------------------------------------------------------------
    """
    def open_tracker(self):
        """PTWorkFlow is the top level class that controls the entire tracking process
        """
        
        self.tracker = PTWorkflow(video_filename=self.movie_filename, param_filename=self.settings_filename, error_reporting=self)
        if hasattr(self, 'viewer_is_setup'):
            self.reset_viewer()


    """
    -------------------------------------------------------------
    -------------------------------------------------------------
    Slots
    --------------------------------------------------------------
    --------------------------------------------------------------
    """

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

        if self.pandas_viewer.isVisible():
            points = self.pandas_viewer.df[['x', 'y']].values
            tree = spatial.KDTree(points)
            dist, idx = tree.query((x, y))
            self.pandas_viewer.view.selectRow(idx)
        
        if self.edit_pandas_viewer.isVisible():
            points = self.edit_pandas_viewer.df[['x', 'y']].values
            tree = spatial.KDTree(points)
            dist, idx = tree.query((x, y))
            self.edit_pandas_viewer.view.selectRow(idx)


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.reset_statusbar)
        self.timer.start(8000)
        self.status_bar.setStyleSheet("background-color : green")
        self.status_bar.showMessage("Coords (x,y): ("+str(x)+','+str(y) +') \t Intensities [r,g,b]:'+str(output[int(y),int(x),:]))    
        self.show()

    @pyqtSlot(int)
    def frame_selector_slot(self, value): 
        try:
            self.update_viewer()
        except:
            msg=QMessageBox(self)
            msg.setText(
            """FYI the software just tried to crash but we caught it! This usually happens
            if the video you load and the current settings file have incompatible frame ranges.
            We've resolved this by resetting the frame_range to the entire video length"""
            )
            msg.show()
            self.reset_frame_range()
        
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
            self.update_dictionary_params(['config','_frame_range'],(0,self.tracker.cap.num_frames-1,1), 'button')
            self.tracker.cap.set_frame_range((0,self.tracker.cap.num_frames,1))
        elif ('frame' in paramdict_location[1]) and (type(value) == tuple):
            frame_range = (self.frame_selector.slider._min,self.frame_selector.slider._max+1,self.frame_selector.slider._step)
            if (frame_range[1] <= self.tracker.cap.num_frames) | (frame_range[1] is None):
                self.update_dictionary_params(['config','_frame_range'],frame_range, 'slider')
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
        that signal in custom_combo_box.py in ComboBoxAndButton.add_method_button_click()
        """
        sender = self.sender()
        location = [sender.title, sender.title + '_method']
        self.update_dictionary_params(location, value, 'list')
        self.update_param_widgets(sender.title)
        self.update_viewer()
        self.update_pandas_view()

    @pyqtSlot(Exception)
    def handle_error(self, error):
        flash_error_msg(error, self)

    """------------------------------------------------------
    Various methods to update sections of the program.
    -------------------------------------------------------"""

    def reset_statusbar(self):
        self.status_bar.setStyleSheet("background-color : lightGray")
        self.status_bar.clearMessage()

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
                                self.tracker.parameters[location[0]][item] = copy.deepcopy(self.tracker.parameters[location[0]][item.split('*')[0]])
                                key_values = list(self.tracker.parameters[location[0]][item].keys())
                                for key in key_values:
                                    if key == 'output_name':
                                        num=item.split('*')[1]
                                        self.tracker.parameters[location[0]][item]['output_name'] = 'classifier*' + num
                                        self.tracker.parameters[location[0]][item]
                        
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
            annotated_img, proc_img = self.tracker.process(f_index=frame_number, lock_part=CustomButton.locked_part)

            toggle = self.toggle_img.isChecked()
            if toggle:
                self.viewer.setImage(bgr_to_rgb(proc_img))
            else:
                self.viewer.setImage(bgr_to_rgb(annotated_img))
            if hasattr(MainWindow, 'pandas_viewer'):
                self.update_pandas_view()

                    
    def reset_viewer(self):
        self.frame_selector.changeSettings(min_=self.tracker.cap.frame_range[0],
                                           max_=self.tracker.cap.frame_range[1] - 1,
                                           step_=1,
                                           )
        self.movie_label.setText(self.movie_filename)
        if hasattr(MainWindow, 'pandas_viewer'):
            self.update_pandas_view()
        if hasattr(MainWindow, 'edit_pandas_viewer'):
            self.update_edit_pandas_view()

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
    
    def open_movie_click(self):
        self.settings_filename = self.tracker.base_filename + '_expt.param'
        write_paramdict_file(self.tracker.parameters, self.settings_filename)
        self.movie_filename = open_movie_dialog(self, self.movie_filename)
        self.reboot()
        
    def open_settings_button_click(self):
        self.settings_filename = open_settings_dialog(self, self.settings_filename)
        self.reboot()    

    def save_settings_button_click(self):
        settings_filename = save_settings_dialog(self, self.settings_filename)
        write_paramdict_file(self.tracker.parameters, settings_filename)
    
    

    """-------------------------------------------------------------
    Functions relevant to the tools section
    --------------------------------------------------------------"""
    
    def setup_pandas_viewer(self):
        if hasattr(self, 'pandas_viewer'):
            self.pandas_viewer.close()
            self.pandas_viewer.deleteLater()
        self.pandas_viewer = PandasWidget(parent=self)
        #self.update_pandas_view()

    def pandas_button_click(self):
        if self.pandas_button.isChecked():
            self.pandas_viewer.show()
        else:
            self.pandas_viewer.hide()

    def update_pandas_view(self):
        path, fname = os.path.split(self.tracker.base_filename)
        fname = path + '/_temp/' + fname +'_temp.hdf5'
        self.pandas_viewer.update_file(fname, self.tracker.cap.frame_num)
    
    def setup_edit_pandas_viewer(self):
        if hasattr(self, 'edit_pandas_viewer'):
            self.edit_pandas_viewer.close()
            self.edit_pandas_viewer.deleteLater()
        self.edit_pandas_viewer = PandasWidget(parent=self, edit=True)
    
    def edit_pandas_button_click(self):
        if self.edit_pandas_button.isChecked():
            self.edit_pandas_viewer.show()
        else:
            self.edit_pandas_viewer.hide()
    
    def update_edit_pandas_view(self):
        print('update_edit_pandas_view not yet implemented')
        path, fname = os.path.split(self.tracker.base_filename)
        locked_id = CustomButton.locked_part
        fname = path + '/_temp/' + fname + CustomButton.extension[locked_id]
        self.pandas_viewer.update_file(fname, self.tracker.cap.frame_num)
      
    def snapshot_button_click(self):
        print('Saving current image to movie file directory...')
        img = qimage2ndarray.byte_view(self.viewer.image())
        n=0
        while n < 1000:
            img_name = self.tracker.base_filename + '_frame' + str(self.frame_selector.value()) + '_' + str(n) +'.png'
            if Path(img_name).is_file():
                n = n+1
            else:
                write_img(img, img_name)
                break
        

        """------------------------------------------------------------
        Functions that control the processing
        --------------------------------------------------------------"""

    def live_update_button_click(self):
        if self.live_update_button.isChecked():
            self.update_viewer()
        self.tracker.parameters['config']['_live_updates'] = self.live_update_button.isChecked()

    def update_lock(self):
        self.tracker.parameters['config']['_locked_part'] = CustomButton.locked_part
        self.tracker.data.clear_caches()
        self.update_viewer()
        self.update_pandas_view()
        self.update_edit_pandas_view()

    def process_button_click(self): 
        self.status_bar.setStyleSheet("background-color : lightBlue")
        self.status_bar.showMessage("Depending on the size of your movie etc this could take awhile. You can track progress in the command window.")    

        self.tracker.reset_annotator()            

        #This is accessing a class variable of CustomButton
        self.tracker.process(lock_part=CustomButton.locked_part)

        self.settings_filename = self.tracker.base_filename + '_expt.param'
        write_paramdict_file(self.tracker.parameters, self.settings_filename)
        
        self.move_final_data()

        self.reset_statusbar()
        QMessageBox.about(self, "", "Processing Finished")
        self.reboot()

    def clean_up(self):
        path, _ = os.path.split(self.movie_filename)
        temp_folder = path + '/_temp'
        CustomButton.reset_lock()
        try:               
            shutil.rmtree(temp_folder)
        except:
            """Remove folder using elevated privileges"""
            if sys.platform == 'win32':
                cmd = f'powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList \'/c rd /s /q \"{folder_path}\"\'\"'
                subprocess.run(cmd, shell=True, check=True)
            else:
                print('Error removing _temp folder')

    def move_final_data(self):
        print('Creating final datafile')
        path, filename = os.path.split(self.movie_filename)
        postprocess_datafile = path + '/_temp/' + filename[:-4] + CustomButton.extension[2]
        output_datafile = path + '/' + filename[:-4] + '.hdf5'

        if os.path.exists(postprocess_datafile):
            shutil.copy(postprocess_datafile, output_datafile)
    


    def close_button_click(self):
        sys.exit()




  
        

        



