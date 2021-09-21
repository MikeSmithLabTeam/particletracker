from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar, QPushButton, QVBoxLayout
import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
import time
 
 
class MyThread(QThread):
    # Create a counter thread
    change_value = pyqtSignal(int)
    def run(self):
        cnt = 0
        while cnt < 100:
            cnt+=1
            time.sleep(0.3)
            self.change_value.emit(cnt)


class ProgressDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.title = "PyQt5 ProgressBar"
        self.top = 200
        self.left = 500
        self.width = 300
        self.height = 100
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        vbox = QVBoxLayout()
        self.progressbar = QProgressBar()
        
        self.progressbar.setMaximum(100)
        self.progressbar.setStyleSheet("QProgressBar {border: 2px solid grey;border-radius:8px;padding:1px}"
                                       "QProgressBar::chunk {background:green}")
        #qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 red, stop: 1 white);
        #self.progressbar.setStyleSheet("QProgressBar::chunk {background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 red, stop: 1 white); }")
        #self.progressbar.setTextVisible(False)
        vbox.addWidget(self.progressbar)
        #self.button.setStyleSheet('background-color:grey')
        self.setLayout(vbox)
        self.progressbar.setValue(0)
        self.show()

    @pyqtSlot(int, int, int, int)    
    def setProgressVal(self, f, start, stop, step):
        range_vals = (float(stop - start) / float(step))
        val = 100*(float(f - start) / range_vals)
        self.progressbar.setValue(int(val))
        self.progressbar.update()
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProgressDialog()
    window.show()
    #Start event loop
    app.exec_()

