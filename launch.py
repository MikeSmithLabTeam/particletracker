#import particletracker as pt
from particletracker import track_gui
from tests.test_integration import test_eyes


if __name__ == '__main__':
    track_gui("testdata/bkg_test")
    #test_eyes()
