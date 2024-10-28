import numpy as np
import scipy.optimize as opt
import pandas as pd

def calibration_fitting(filepath, filename, *args, **kwargs):
    """Function to fit a polynomial to given accelerometer calibration data.
    Takes filepath to .csv file, reads into a pandas dataframe, converts to
    numpy array then performs fit using scipy.optimize.curve_fit.
    Saves fit parameters to "calibration_fit_param.txt" file in the 
    MikeSmithLabSharedFolder.

    Args:
        filepath : filepath input given by particletracker user. 
        filename : name of calibration data file
    Returns:
        None
    """    
    func = lambda x,a,b,c,d,e, : a*x**4 + b*x**3 + c*x**2 + d*x + e

    calibration_data = pd.read_csv(str(filepath)+'/'+str(filename))
    cal_arr = calibration_data.to_numpy()
    acc_data, duty_data = cal_arr[:,1], cal_arr[:,0]
    popt, pcov = opt.curve_fit(func, duty_data, acc_data)
    np.savetxt("Z:/shaker_config/calibration_fit_param.txt", popt)
    return None
