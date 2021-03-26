from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPixmap, QImage, QPainterPath, QCloseEvent, QWheelEvent, QColor
from PyQt5.QtWidgets import (QWidget, QSlider, QCheckBox, QHBoxLayout,
                             QLabel, QComboBox, QSizePolicy, QVBoxLayout,
                             QApplication, QGraphicsView, QGraphicsScene,
                             QLineEdit
                             )
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, \
    NavigationToolbar2QT
from matplotlib.figure import Figure

from qtwidgets import QCustomTextBox, SelectAreaWidget

from ..general.parameters import parse_values
from ..customexceptions import *


class QModCustomTextBox(QCustomTextBox):
    returnPressed = pyqtSignal(str)

    def __init__(self, img_viewer, parent=None, *args, **kwargs):
        if parent is not None:
            self.parent=parent
        self.img_viewer = img_viewer
        shapes = {'crop_box':['rect',QColor(250, 10, 10, 80)],
                  'mask_ellipse':['ellipse',QColor(10,10,250,80)],
                  'mask_polygon':['polygon',QColor(10,10,250,80)],
                  'mask_circle':['circle', QColor(10,10,250,80)],
                  'mask_rectangle':['rect', QColor(10,10,250,80)],
                  }
        title=kwargs['title'].split('*')[0]
        self.method = shapes[title][0]
        self.colour = shapes[title][1]
        self.hasbeenchecked = False#Stops the checkboxChanged fn firing on object creation.
        super(QModCustomTextBox, self).__init__(*args, **kwargs)
        self.checkbox.setChecked(False)
        self.widget='textbox'
        
    def checkboxChanged(self) -> None:
        #Override checkboxChanged method
        check_state = self.checkbox.isChecked()
        
        if check_state:
            points = parse_values(self, self.value())
            if points is not None:
                points = list(points)
            self.tool = SelectAreaWidget(shape=self.method, viewer=self.img_viewer, colour=self.colour, points=points, handle_rad=10)
            self.img_viewer.scene.addWidget(self.tool)
            self.hasbeenchecked = True
        else:
            if self.hasbeenchecked:
                try:
                    #Catches checking and unchecking text box without using tool
                    self.textbox.setText(str(tuple(self.tool.points)))
                    self.returnPressed.emit(str(tuple(self.tool.points)))   
                except Exception as e:
                    e=CropMaskError(e)
                    flash_error_msg(e, self.parent)
                    
                self.tool.setParent(None)
                self.tool.deleteLater()
            self.hasbeenchecked = False
