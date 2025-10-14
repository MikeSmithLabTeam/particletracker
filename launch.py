# import particletracker as pt
from particletracker import track_gui, batchprocess
import os


if __name__ == '__main__':
    userprofile = os.environ['USERPROFILE']
    path = userprofile + \
        "\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\testdata\\"
    
    track_gui("testdata/hydrogel.mp4", "testdata/test_networks.param")
