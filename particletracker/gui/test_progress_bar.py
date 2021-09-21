from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
from progress_bar import ProgressDialog

from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar, QPushButton, QVBoxLayout
import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
import time

class window(QMainWindow):
    def __init__(self):
        self.prog = ProgressDialog()
        




App = QApplication(sys.argv)
window = window()

sys.exit(App.exec())