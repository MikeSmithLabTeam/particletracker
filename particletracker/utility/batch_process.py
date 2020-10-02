from filehandling import BatchProcess
from ..project.workflow import PTProject


if '__main__' == __name__:

    filefilter = '/home/mike/PycharmProjects/ParticleTracker/testdata/contours.mp4'
    #Use wildcard characters to select multiple files eg testdata/*.mp4 but be careful about
    #existing annotation files in folder.
    paramfile = '/home/mike/PycharmProjects/ParticleTracker/project/param_files/contours_hydrogels.param'



    for filename in BatchProcess(filefilter):
        track = PTProject(video_filename=filename, param_filename=paramfile)
        track.crop_select = True
        track.preprocess_select = True
        track.track_select = True
        track.link_select = True
        track.postprocess_select = False
        track.annotate_select = True
        track.process()