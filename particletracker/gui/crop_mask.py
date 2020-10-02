from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class SelectAreaWidget(QWidget):
    def __init__(self, shape=None, geometry=None, colour=QColor(250, 10, 10, 80)):
        self.shape=shape
        self.points = []
        self.display_point_list = []
        self.colour=colour
        super().__init__()
        self.setGeometry(geometry)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.transparent)
        self.setPalette(p)
        self.begin = QPoint()
        self.end = QPoint()

    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(self.colour)
        qp.setBrush(br)

        if self.shape == 'rect':
            qp.drawRect(QRect(self.begin, self.end))
        elif self.shape == 'mask_ellipse':
            qp.drawEllipse(QRect(self.begin, self.end))
            self.ellipse_pts = ((self.begin.x(),self.begin.y()),(self.end.x(),self.end.y()))
        elif self.shape == 'mask_polygon':
            points=QPolygon(self.points)
            qp.drawPolygon(points)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        if self.shape == 'mask_polygon':
            self.points.append(QPoint(self.begin.x(),self.begin.y()))
            self.display_point_list.append((self.begin.x(),self.begin.y()))
        elif self.shape == 'mask_ellipse':
            self.update()
        else:
            self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.update()


if __name__ == '__main__':
    import sys
    app = QApplication([])
    window = SelectAreaWidget(shape='rect')
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())