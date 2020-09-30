from matplotlib import pyplot as plt
from matplotlib.widgets import RectangleSelector
import time

from ParticleTracker.gui.pyqt5_widgets import MatplotlibFigure


class ROIGraph(MatplotlibFigure):
    def __init__(self, parent, img):
        MatplotlibFigure.__init__(self, parent)
        self.img=img
        self.setup_axes()
        self.initial_plot()

    def setup_axes(self):
        self.ax = self.fig.add_subplot(111)

    def initial_plot(self):
        time.sleep(0.1)
        self.ax.imshow(self.img,cmap='gray')
        self.RoiFig = ROIfigure(self.ax)

class ROIfigure():

    def __init__(self,img,coords=None):
        self.img=img
        self.coords=coords
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.imshow(img)
        self.rec = self.CreateRectangle()
        self.rec.to_draw.set_visible(True)
        plt.show()

    def CreateRectangle(self):
        rec = RectangleSelector(self.ax, self.rectangle_callback, drawtype= 'box'
                                , useblit= False, button= [1,3], minspanx=5, minspany=5,
                                spancoords='data', interactive = True)
        return rec

    def rectangle_callback(self,eclick,erelease):
        self.x1, self.y1 = eclick.xdata, eclick.ydata
        self.x2, self.y2 = erelease.xdata, erelease.ydata
        self.width = int(self.x2 - self.x1)
        self.height = int(self.y2 - self.y1)
        self.xoff = int(self.x1)
        self.yoff = int(self.y1)
        self.rec.extents = (self.xoff, self.xoff + self.width, self.yoff, self.yoff + self.height)
        self.coords=(self.xoff,self.yoff,self.width,self.height)





if __name__ == '__main__':
    import cv2

    filename = '/home/mike/Pictures/2019_10_14_16_32_40.png'

    img = cv2.imread(filename)

    #fig = plt.figure()
    #ax = fig.add_subplot(111)

    #ax.imshow(img,cmap='gray')
    roi = ROIfigure(img)
    plt.show()