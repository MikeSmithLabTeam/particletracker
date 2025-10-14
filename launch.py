#import particletracker as pt
from particletracker import track_gui
from tests.test_integration import test_eyes
from particletracker import batchprocess

if __name__ == '__main__':
    #track_gui("testdata/bkg_test")
    #test_eyes()

    moviefilter = 'E:/RawData/Oliver/orderphobic/Intruders/2025_10_13/630_1/*.mp4'
    settings = 'E:/RawData/Oliver/orderphobic/Intruders/2025_10_10/param.param'
    batchprocess(moviefilter, settings)