# import particletracker as pt
from particletracker import track_gui, batchprocess
import os


if __name__ == '__main__':
    userprofile = os.environ['USERPROFILE']
    path = userprofile + \
        "\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\testdata\\"
    
    print(path)
    #track_gui(path + "hydrogel.mp4",settings_filename=path +"hydrogel1.param")
    track_gui("testdata/bacteria.mp4", "testdata/test_bacteria.param")
    
    # test_eyes()
