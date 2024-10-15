import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import webbrowser
from PyQt5.QtCore import QSize
from .file_io import save_snapshot, open_movie_dialog, open_settings_dialog, save_settings_dialog, create_default_settings_filepath
from ..general.param_file_creator import create_param_file
from .pandas_view import PandasWidget

class MenuBar:
    def __init__(self, main_gui):
        self.gui = main_gui
        dir,_ =os.path.split(os.path.abspath(__file__))
        resources_dir = os.path.join(dir,'icons','icons')
        #Use these lines when using pyinstaller.
        #dir , _= os.path.split(sys.argv[0])#os.path.abspath(__file__)
        #resources_dir = os.path.join(dir,'gui','icons','icons')
        self.toolbar = QToolBar('Toolbar')
        self.toolbar.setIconSize(QSize(16,16))
        main_gui.addToolBar(self.toolbar)

        '''
        ---------------------------------------------------------------------------------------------------
        Buttons on toolbar
        ---------------------------------------------------------------------------------------------------
        '''
        open_movie_button = QAction(QIcon(os.path.join(resources_dir,"folder-open-film.png")), "Open File", main_gui)
        open_movie_button.setStatusTip("Open Movie")
        open_movie_button.triggered.connect(self.open_movie_click)
        self.toolbar.addAction(open_movie_button)

        open_settings_button = QAction(QIcon(os.path.join(resources_dir,"script-import.png")), "Open Settings File", main_gui)
        open_settings_button.setStatusTip("Open Movie")
        open_settings_button.triggered.connect(self.open_settings_button_click)
        self.toolbar.addAction(open_settings_button)

        save_settings_button = QAction(QIcon(os.path.join(resources_dir,"script-export.png")), "Save Settings File", main_gui)
        save_settings_button.setStatusTip("Save Settings")
        save_settings_button.triggered.connect(self.save_settings_button_click)
        self.toolbar.addAction(save_settings_button)

        self.autosave_on_process = QAction(QIcon(os.path.join(resources_dir,"autosave.png")), 'Autosave settings on process', main_gui)
        self.autosave_on_process.setCheckable(True)
        self.autosave_on_process.setChecked(main_gui.tracker.parameters['config']['autosave_settings'])
        self.autosave_on_process.triggered.connect(self.autosave_button_click)
        self.toolbar.addAction(self.autosave_on_process)

        self.toolbar.addSeparator()

        self.live_update_button = QAction(QIcon(os.path.join(resources_dir,"arrow-circle.png")), "Live Updates", main_gui)
        self.live_update_button.setCheckable(True)
        self.live_update_button.setChecked(main_gui.tracker.parameters['config']['live_updates'])
        self.live_update_button.triggered.connect(self.live_update_button_click)
        self.toolbar.addAction(self.live_update_button)

        self.pandas_button = QAction(QIcon(os.path.join(resources_dir, "view_pandas.png")),"Show Dataframe View", main_gui)
        self.pandas_button.triggered.connect(self.pandas_button_click)
        self.pandas_button.setCheckable(True)
        self.pandas_button.setChecked(False)
        self.toolbar.addAction(self.pandas_button)

        self.snapshot_button = QAction(QIcon(os.path.join(resources_dir, "camera.png")),"Take snapshot", main_gui)
        self.snapshot_button.triggered.connect(self.snapshot_button_click)
        self.toolbar.addAction(self.snapshot_button)

        self.toolbar.addSeparator()

        self.export_to_csv = QAction(QIcon(os.path.join(resources_dir,"excel.png")),'Export to csv', main_gui)
        self.export_to_csv.setCheckable(True)
        self.export_to_csv.setChecked(main_gui.tracker.parameters['config']['csv_export'])
        self.export_to_csv.triggered.connect(self.export_to_csv_click)
        self.toolbar.addAction(self.export_to_csv)

        process_part_button = QAction(QIcon(os.path.join(resources_dir,"clapperboard--minus.png")), "Process part", main_gui)
        process_part_button.triggered.connect(self.process_part_button_click)
        self.toolbar.addAction(process_part_button)

        self.use_part_button = QAction(QIcon(os.path.join(resources_dir,"fire--exclamation.png")), "Use part processed", main_gui)
        self.use_part_button.setCheckable(True)
        self.use_part_button.triggered.connect(self.use_part_button_click)
        self.toolbar.addAction(self.use_part_button)

        process_button = QAction(QIcon(os.path.join(resources_dir,"clapperboard--arrow.png")), "Process", main_gui)
        process_button.triggered.connect(self.process_button_click)
        self.toolbar.addAction(process_button)

        self.toolbar.addSeparator()

        close_button = QAction(QIcon(os.path.join(resources_dir,"cross-button.png")), "Close", main_gui)
        close_button.triggered.connect(self.close_button_click)
        self.toolbar.addAction(close_button)

        menu = main_gui.menuBar()

        self.status_bar = QStatusBar(main_gui)
        font = QFont()
        font.setPointSize(14)
        self.status_bar.setFont(font)
        main_gui.setStatusBar(self.status_bar)
        

        '''
        ---------------------------------------------------------------------------------------------
        File menu items
        ---------------------------------------------------------------------------------------------
        '''
        self.file_menu = menu.addMenu("&File")
        self.tool_menu = menu.addMenu("Tools")
        self.process_menu = menu.addMenu("Process options")
        self.help_menu = menu.addMenu("Help")

        load_defaults = QAction('Load default settings', main_gui)
        load_defaults.triggered.connect(self.load_default_settings)

        self.file_menu.addAction(open_movie_button)
        self.file_menu.addAction(open_settings_button)
        self.file_menu.addAction(save_settings_button)
        self.file_menu.addAction(load_defaults)
        self.file_menu.addSeparator()
        self.file_menu.addAction(close_button)

        self.tool_menu.addAction(self.live_update_button)
        self.tool_menu.addAction(self.pandas_button)
        self.tool_menu.addAction(self.snapshot_button)

        self.process_menu.addAction(self.autosave_on_process)
        self.process_menu.addAction(self.export_to_csv)
        self.process_menu.addAction(process_part_button)
        self.process_menu.addAction(self.use_part_button)
        self.process_menu.addAction(process_button)

        docs = QAction('help', main_gui)
        docs.triggered.connect(self.open_docs)
        about = QAction('about', main_gui)
        about.triggered.connect(self.about)

        self.help_menu.addAction(docs)
        self.help_menu.addAction(about)

        self.setup_pandas_viewer()   

    def load_default_settings(self):
        self.gui.settings_filename = create_default_settings_filepath(self.gui.movie_filename)
        create_param_file(self.gui.settings_filename)
        self.gui.reboot()
       
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

    """--------------------------------------------------------------------------------
    Call back functions associated with menubar
    --------------------------------------------------------------------------------"""

    def snapshot_button_click(self):
        save_snapshot(self.gui)

    def open_movie_click(self):
        self.movie_filename = open_movie_dialog(self.gui, self.movie_filename)
        main_gui.reboot()
        
    def open_settings_button_click(self):
        self.settings_filename = open_settings_dialog(self.gui, self.settings_filename)
        main_gui.reboot()    

    def save_settings_button_click(self):
        settings_filename = save_settings_dialog(self.gui, self.settings_filename)
        write_paramdict_file(self.gui.tracker.parameters, settings_filename)

    def export_to_csv_click(self):
        self.gui.tracker.parameters['config']['csv_export'] = self.export_to_csv.isChecked()

    """-------------------------------------------------------------
    Functions relevant to the tools section
    --------------------------------------------------------------"""

    def setup_pandas_viewer(self):
        if hasattr(self, 'pandas_viewer'):
            self.pandas_viewer.close()
            self.pandas_viewer.deleteLater()
        self.pandas_viewer = PandasWidget(parent=self)

    def pandas_button_click(self):
        if self.pandas_button.isChecked():
            self.pandas_viewer.show()
        else:
            self.pandas_viewer.hide()

    def update_pandas_view(self):
        fname = self.gui.tracker.data_filename
        if not self.use_part_button.isChecked():
            fname = fname[:-5] +'_temp.hdf5'
        self.pandas_viewer.update_file(fname, self.gui.tracker.cap.frame_num)
 
        """------------------------------------------------------------
        Functions that control the processing
        --------------------------------------------------------------"""
    def autosave_button_click(self):
        main_gui.tracker.parameters['config']['autosave_settings'] = self.autosave_on_process.isChecked()

    def live_update_button_click(self):
        if self.live_update_button.isChecked():
            main_gui.update_viewer()
        main_gui.tracker.parameters['config']['live_updates'] = self.live_update_button.isChecked()

    def process_part_button_click(self):
        '''
        This button processes the movie but it skips the postprocess and annotation steps
        It is designed as a first step to experiment with different postprocessing and
        and annotation steps. Some of these require data from other frames which is not
        possible if you just process a single frame. To then process that data you need
        to check the use_part_button.
        '''
        postprocess_init_state = main_gui.tracker.postprocess_select
        annotate_init_state = main_gui.tracker.postprocess_select
        main_gui.tracker.postprocess_select = False
        main_gui.tracker.annotate_select = False
        main_gui.process_button_click()
        main_gui.tracker.postprocess_select = postprocess_init_state
        main_gui.tracker.annotate_select = annotate_init_state

    def use_part_button_click(self):
        '''This code only changes appearance of gui and checks
        to see if .hdf5 data file exists. The commands tracker.process
        and tracker.process_frame take a keyword use_part which
        is set by checking toggle status of this button.
        '''
        if isfile(main_gui.tracker.data_filename):
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
            write_paramdict_file(main_gui.tracker.parameters, self.settings_filename)

        if self.use_part_button.isChecked():
            main_gui.tracker.process(use_part=True)
        else:
            main_gui.tracker.process()

        write_paramdict_file(main_gui.tracker.parameters, main_gui.tracker.data_filename[:-5] + '_expt.param')
        
        self.reset_statusbar()
        QMessageBox.about(self, "", "Processing Finished")
        self.reboot(open_settings=False)

    def close_button_click(self):
        sys.exit()