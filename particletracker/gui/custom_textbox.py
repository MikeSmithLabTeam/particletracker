from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPixmap, QImage, QPainterPath, QCloseEvent, QWheelEvent, QColor
from PyQt6.QtWidgets import (QWidget, QSlider, QCheckBox, QHBoxLayout,
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
    """
    This widget is the text box with checkbox used for
    the crop and mask tools interface at bottom right of gui.
    Key functionality for the dragging shapes on the image
    is provided by SelectAreaWidget from qtwidgets repo.
    """
    returnPressed = pyqtSignal(str)
    errorOccurred = pyqtSignal(Exception)

    def __init__(self, img_viewer, *args, **kwargs):
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
                    self.errorOccurred.emit(e)
                    
                self.tool.setParent(None)
                self.tool.deleteLater()
            self.hasbeenchecked = False
