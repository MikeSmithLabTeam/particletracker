from particletracker import track_gui
from tests.test_integration import test_eyes
from particletracker.general.parameters import get_parent

import particletracker

if __name__ == '__main__':
    track_gui("testdata/hydrogel.mp4", "testdata/test_postprocess.param")
    #test_eyes()
