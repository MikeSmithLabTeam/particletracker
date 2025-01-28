import numpy as np
import pandas as pd
from particletracker.postprocess.postprocessing_methods import hexatic_order
import scipy.spatial as sp

def test_hexatic_order():
    """Testing that the hexatic_order() function in particle 
     tracker postprocessing methods works. Has the param parse
      decorator attached. """
    
    param = {'postprocess':{'hexatic_order':{
            'cutoff':[5]}}}
    
    data = pd.read_hdf("testdata/hexatic_test_data.hdf5")
    data = hexatic_order(data, f_index=0, parameters=param, call_num=None, section='postprocess')
    hexatic_col = data["hexatic_order"]
    value = hexatic_col.iloc[[3][0]]    #pick particle away from edge
    assert int(np.real(value)) == 1
    assert int(np.imag(value)) == 0