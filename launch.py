# import particletracker as pt
from particletracker import track_gui
import os


if __name__ == '__main__':
    userprofile = os.environ['USERPROFILE']
    path = userprofile + \
        "\\OneDrive - The University of Nottingham\\Documents\\Programming\\particletracker\\testdata\\"
    # , settings_filename=path + "test.param")
    track_gui(path + "hydrogel.mp4")
    # test_eyes()
