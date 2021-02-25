from ..project import PTWorkflow
from ..general.writeread_param_dict import read_paramdict_file
from filehandling import BatchProcess


class PTProject(PTWorkflow):
    '''
    PTProject is a daughter class which is used as the interface to a particle tracking project.

    Setup
    -----

    Select which bits of the process you are interested in by setting the Boolean
    Operators. You read a dictionary PARAMETERS which controls all of the settings.
    It is up to you to make sure you have the correct parameters.

    Create an "instance" of the class:
    track=PTProject(video_filename="Full Path To File")

    Examples
    --------

    There are 2 main approaches:
    1) Pass the instance as an argument to TrackGui to optimise/trial things

    | track = PTProject(video_filename='/home/mike/Documents/HydrogelTest.m4v')
    | TrackingGui(track)

    2) call "instance".process() to process an entire movie.

    | track = PTProject(video_filename='/home/mike/Documents/HydrogelTest.m4v')
    | track.process()

    Use method 1 to optimise the process and method 2 to process afterwards.

    You can select the various parts of the operation by setting the flags to self.process_select

    | self.preprocess_select = True
    | self.track_select = True
    | self.postprocess_select = False
    | self.annotate_select = True

    What these processes will do is governed by the respective parts of the PARAMETERS dictionary above

    '''

    def __init__(self, video_filename=None, param_filename=None, parent=None):
        #Select operations to be performed'output_name':'x_smooth',
        PTWorkflow.__init__(self, video_filename=video_filename, parent=parent)
        self.crop_select = True
        self.preprocess_select = True
        self.track_select = True
        self.link_select = True
        self.postprocess_select = False
        self.annotate_select = False
        self.param_filename = param_filename

        self.parameters = read_paramdict_file(param_filename)
        self._setup()


