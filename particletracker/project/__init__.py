import os.path

from ..video_crop import ReadCropVideo
from .. import tracking, preprocessing, postprocessing, \
    annotation, linking

class PTWorkflow:
    '''
    PTWorkflow is a parent class that handles the workflow of a particle tracking project.
    '''

    def __init__(self, video_filename=None):
        self.video_filename = video_filename
        self.filename = os.path.splitext(self.video_filename)[0]
        self.data_filename = self.filename + '.hdf5'

        #These should be overwritten in child class
        self.crop_select = False
        self.preprocess_select = False
        self.track_select = False
        self.link_select = False
        self.postprocess_select = False
        self.annotate_select = False

        self.parameters = {}

    def _setup(self):
        ''' Setup is a internal class method it instantiates the reader object
        Depending on the settings in PARAMETERS this may also crop the video frames
        as they are requested.'''
        self.parameters['experiment']['video_filename'] = self.video_filename
        self._create_processes()

    def _create_processes(self):
        self.cap = ReadCropVideo(parameters=self.parameters['crop'],
                                 filename=self.video_filename,
                                 )
        self.ip = preprocessing.Preprocessor(self.parameters)
        self.pt = tracking.ParticleTracker(
            parameters=self.parameters['track'], preprocessor=self.ip,
            vidobject=self.cap, data_filename=self.data_filename)
        self.link = linking.LinkTrajectory(
            data_filename=self.data_filename,
            parameters=self.parameters['link'])
        self.pp = postprocessing.PostProcessor(
            data_filename=self.data_filename,
            parameters=self.parameters['postprocess'])
        self.an = annotation.TrackingAnnotator(vidobject=self.cap,
                                               data_filename=self.data_filename,
                                               parameters=self.parameters[
                                                   'annotate'], frame=self.cap.read_frame())
        self.frame = self.cap.read_frame()

    def reset_annotator(self):
        self.an = annotation.TrackingAnnotator(vidobject=self.cap,
                                                       data_filename=self.data_filename,
                                                       parameters=self.parameters[
                                                           'annotate'], frame=self.cap.read_frame())

    def process(self, use_part=False):
        """Process an entire video

        Process is called on the main instance using the command
        particle_tracking_instance.process(). One call results in the entire
        movie being processed according to the actions selected in the child class.
        i.e track = True
            link = True etc
        :return:
        """
        if not use_part:
            if self.track_select:
                self.pt.track()
            if self.link_select:
                self.link.link_trajectories()
        if self.postprocess_select:
            self.pp.process(use_part=True)
        if self.annotate_select:
            self.an.annotate(use_part=use_part)



    def process_frame(self, frame_num, use_part=False):
        """Process a single frame

        process_frame() is for use with the tracking guis when
        optimising parameters. It takes the frame indicated by
        frame_num and processes it according to the selected actions.
        ie. track=True, link=True

        Notes
        -----

        Some combinations of actions are not possible. e.g you can't link trajectories
        that haven't been tracked! The software will however allow you to do things progressively
        so that if you have previously tracked a video and it has sucessfully written to a dataframe
        then it will subsequently link that data without needing to retrack the video.
        The same logic applies to annotation etc. It is worth however making backups at various points.
        When processing individual frames the data is temporarily stored in videoname_temp.hdf5 However, during
        process_part or process the data is stored in videoname.hdf5

        The software assumes the datastore is in the same folder as the video being processed.

        If use_part = True the data for first 5 stages is read from file and only postprocess and annotate are
        being run.

        """
        if not use_part:
            if self.preprocess_select:
                frame=self.cap.read_frame(frame_num)
                proc_frame = self.ip.process(frame)
                proc_frame = self.cap.apply_mask(proc_frame)
            else:
                proc_frame = self.cap.read_frame(frame_num)
            if self.track_select:
                self.pt.track(f_index=frame_num)
            if self.link_select:
                self.link.link_trajectories(f_index=frame_num)

        if self.postprocess_select:
            self.pp.process(f_index=frame_num, use_part=use_part)
        if self.annotate_select:
            annotatedframe = self.an.annotate(f_index=frame_num, use_part=use_part)
            if use_part:
                proc_frame = self.cap.read_frame(frame_num)
        else:
            annotatedframe = self.cap.read_frame(frame_num)
            if use_part:
                proc_frame = annotatedframe
        return annotatedframe, proc_frame

