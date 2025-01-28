import sys
import os

# Add the testdata directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../testdata')))

import warnings 
from pandas.errors import PerformanceWarning

warnings.filterwarnings("ignore", message="PeformanceWarning*", category=PerformanceWarning)

    

