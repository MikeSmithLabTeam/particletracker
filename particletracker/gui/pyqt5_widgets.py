import sys
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPixmap, QImage, QPainterPath, QCloseEvent, QWheelEvent, QColor
from PyQt5.QtWidgets import (QWidget, QSlider, QCheckBox, QHBoxLayout,
                             QLabel, QComboBox, QSizePolicy, QVBoxLayout,
                             QApplication, QGraphicsView, QGraphicsScene,
                             QLineEdit
                             )
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, \
    NavigationToolbar2QT
from matplotlib.figure import Figure

from qtwidgets import QCustomTextBox, SelectAreaWidget


class QModCustomTextBox(QCustomTextBox):
    returnPressed = pyqtSignal(str)

    def __init__(self, img_viewer, *args, **kwargs):
        self.img_viewer = img_viewer
        shapes = {'crop_box':['rect',QColor(250, 10, 10, 80)],
                  'mask_ellipse':['ellipse',QColor(10,10,250,80)],
                  'mask_polygon':['polygon',QColor(10,10,250,80)]
                  }
        title=kwargs['title']
        self.method = shapes[title][0]
        self.colour = shapes[title][1]
        print('created')
        self.hasbeenchecked = False#Stops the checkboxChanged fn firing on object creation.
        print(self.hasbeenchecked)
        super(QModCustomTextBox, self).__init__(*args, **kwargs)
        self.checkbox.setChecked(False)


    def checkboxChanged(self) -> None:
        #Override checkboxChanged method
        check_state = self.checkbox.isChecked()
        if check_state:
            print('checkstate')
            self.tool = SelectAreaWidget(shape=self.method, geometry=self.img_viewer.geometry, colour=self.colour)
            self.img_viewer.scene.addWidget(self.tool)
            self.hasbeenchecked = True
        else:
            print('tool')

            if self.hasbeenchecked:
                self.textbox.setText(str(tuple(self.tool.points)))
                self.returnPressed.emit(self.text)
                self.tool.setParent(None)
                self.tool.deleteLater()
            self.hasbeenchecked = False




class Slider(QWidget):

    def __init__(
            self,
            parent,
            label,
            function,
            start=0,
            end=10,
            dpi=1,
            initial=0):
        initial *= dpi
        start *= dpi
        end *= dpi

        self._function = function
        self._dpi = dpi
        self._sliderValue = initial
        self._value = initial
        self._start = start
        self._end = end

        QWidget.__init__(self, parent)

        lbl = QLabel(label, parent=self)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(start, end)
        self.slider.setSliderPosition(initial)
        self.slider.valueChanged[int].connect(self.sliderCallback)
        self.slider.setTickPosition(QSlider.TicksBelow)

        self.lbl = QLabel(str(initial / dpi), self)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(lbl)
        self.layout().addWidget(self.slider)
        self.layout().addWidget(self.lbl)

    def sliderCallback(self, value):
        value = self.calculateValue(value)
        if self.value() is not None:
            self.setValue(value)
        self.setSliderValue(value)
        self.callFunction()

    def setValue(self, value):
        self._value = value

    def value(self):
        return self._value

    def setSliderValue(self, value):
        self._sliderValue = value
        self.lbl.setText(str(value))
        
    def setSliderRangeValues(self, start, end):
        self.slider.setRange(start, end)

    def sliderValue(self):
        return self._sliderValue

    def calculateValue(self, value):
        return value / self._dpi

    def callFunction(self):
        self._function(self.value())


class CheckedSlider(Slider):

    def __init__(
            self,
            parent,
            label,
            function,
            **kwargs):
        Slider.__init__(self, parent, label, function, **kwargs)
        self.check=None
        self.setValue(self.check)
        self.checkbox = QCheckBox(self)
        self.checkbox.stateChanged.connect(self.checkboxCallback)
        self.layout().addWidget(self.checkbox)

    def checkboxCallback(self, state):
        if state == Qt.Checked:
            self.check=True
            self.setValue(self.sliderValue())
        else:
            self.check=False
            self.setValue(None)
        self.callFunction()


class ArraySlider(Slider):

    def __init__(self, parent, label, function, array):
        start = 0
        end = len(array) - 1
        dpi = 1
        initial = 0
        Slider.__init__(self, parent, label, function,
                        start=start, end=end, dpi=dpi,
                        initial=initial)
        self.array = array

    def calculateValue(self, value):
        return self.array[value]

class LblEdit(QWidget):
    def __init__(self, parent, label, initial, function):
        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())
        self.value=str(initial)
        self.function = function
        self.lbl = QLabel(label, parent)
        self.edit = QLineEdit(parent)
        self.edit.setText(self.value)
        self.edit.returnPressed.connect(self.edit_callback)
        self.layout().addWidget(self.lbl)
        self.layout().addWidget(self.edit)

    def edit_callback(self):
        self.value = int(self.edit.text())
        self.function(self.value)

class ComboBox(QWidget):

    def __init__(self, parent, label, items, function):
        QWidget.__init__(self, parent)

        lbl = QLabel(label, parent)
        combo = QComboBox(parent)
        combo.addItems(items)
        combo.activated[str].connect(function)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(lbl)
        self.layout().addWidget(combo)
        self.layout().addStretch(1)


class CheckBox(QCheckBox):
    def __init__(self, parent, label, function, initial='off'):
        QCheckBox.__init__(self, label, parent)
        self.stateChanged.connect(function)
        if initial == 'on':
            self.setCheckState(Qt.Checked)


class MatplotlibFigure(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())
        self.canvas = PlotCanvas(self)
        self.fig = self.canvas.fig
        self.draw = self.canvas.draw
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)


class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent):
        self.fig = Figure()
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvasQTAgg.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)


class QWidgetMod(QWidget):
    """
    Overrides the closeEvent method of QWidget to print out the parameters set
    in the gui. Is used by ParamGui.
    """
    def __init__(self,param_dict):
        QWidget.__init__(self)
        self.param_dict = param_dict

    def closeEvent(self, a0: QCloseEvent) -> None:
        print('Final Parameters')
        print('------------------------------')
        for key in sorted(self.param_dict.keys()):
            print(key + ' : ' +  str(self.param_dict[key][0]))
        print('------------------------------')

class QtImageViewer(QGraphicsView):
    """ PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.
    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).
    To display any other image format, you must first convert it to a QImage or QPixmap.
    Some useful image format conversion utilities:
        qimage2ndarray: NumPy ndarray <==> QImage    (https://github.com/hmeine/qimage2ndarray)
        ImageQt: PIL Image <==> QImage  (https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)
    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.

        __author__ = "Marcel Goldschen-Ohm <marcel.goldschen@gmail.com>"
    """

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    leftMouseButtonPressed = pyqtSignal(float, float)
    rightMouseButtonPressed = pyqtSignal(float, float)
    leftMouseButtonReleased = pyqtSignal(float, float)
    rightMouseButtonReleased = pyqtSignal(float, float)
    leftMouseButtonDoubleClicked = pyqtSignal(float, float)
    rightMouseButtonDoubleClicked = pyqtSignal(float, float)
    scrollMouseButton = pyqtSignal(float)

    def __init__(self):
        QGraphicsView.__init__(self)

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspectRatioMode = Qt.KeepAspectRatio

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = True

    def hasImage(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None

    def clearImage(self):
        """ Removes the current image pixmap from the scene if it exists.
        """
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")
        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))  # Set scene size to image size.
        self.updateViewer()

    def updateViewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], Qt.KeepAspectRatio)# Qt.IgnoreAspectRatio)  # Show zoomed rect (ignore aspect ratio).
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        self.updateViewer()

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            if self.canPan:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """
        QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QPainterPath())  # Clear current selection area.
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()
            self.setDragMode(QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

    def mouseDoubleClickEvent(self, event):
        """ Show entire image.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.zoomStack = []  # Clear zoom stack.
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mouseDoubleClickEvent(self, event)
        
    def wheelEvent(self, event: QWheelEvent):
        self.scrollMouseButton.emit(int(event.angleDelta().y()/120))
        QGraphicsView.wheelEvent(self, event)
        
                
        
if __name__ == "__main__":
    import numpy as np

    # Matplotlib Example
    app = QApplication(sys.argv)

    main = MatplotlibFigure(None)
    main.ax = main.fig.add_subplot(111)
    x = np.arange(10)
    y = x ** 2
    main.ax.plot(x, y)
    main.draw()
    main.show()

    sys.exit(app.exec_())
