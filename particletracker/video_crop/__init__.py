import numpy as np
import cv2

#from .crop_methods import crop_box
from labvision.video import ReadVideo


class ReadCropVideo(ReadVideo):

    def __init__(self, parameters=None, filename=None, frame_range=(0,None,1)):
        ReadVideo.__init__(self, filename=filename, frame_range=frame_range)
        self.parameters = parameters
        '''
        If loading a new video with different dimensions,
        then the stored crop and mask parameters may not fit.
        Perform a check. If fails reset crop and mask to frame
        dimensions. This may not sort the gui but it will stop
        a crash.
        '''
        crop_height = self.parameters['crop_box'][1][1] - self.parameters['crop_box'][1][0]
        crop_width = self.parameters['crop_box'][0][1] - self.parameters['crop_box'][0][0]
        if (self.height < crop_height) or (self.width < crop_width):
            self.reset()

        self.set_mask()   

    def reset(self):
        #To set crop back to max image size
        self.parameters['crop_box']=((0, 0),(self.width, self.height))
        self.mask_none()

    def set_mask(self):
        if 'mask_ellipse' in self.parameters['crop_method']:
            ellipse_pts = self.parameters['mask_ellipse']
            self.mask_ellipse(ellipse_pts)
        elif 'mask_polygon' in self.parameters['crop_method']:
            points = self.parameters['mask_polygon']
            self.mask_polygon(points)
        else:
            self.mask_none()
    
    def mask_ellipse(self, ellipse_pts):
        #calculate mask given ellipse pts
        if ellipse_pts is None:
            self.mask_none()
        else:
            self.mask_none()
            img=~self.mask
            pts = ellipse_pts
            ellipse = np.array([[pts[0][0],pts[0][1]],[pts[0][0],pts[1][1]],[pts[1][0],pts[1][1]],[pts[1][0],pts[0][1]]])
            rect=cv2.minAreaRect(ellipse)
            ellipse_mask = cv2.ellipse(img,rect,255,thickness=-1)
            self.mask = ellipse_mask

    def mask_polygon(self, point_list):
        #calculate mask given points
        if point_list is None:
            self.mask_none()
        else:
            self.mask_none()
            img=~self.mask
            poly = []
            for point in point_list:
                poly.append([point[0],point[1]])
            self.mask = cv2.fillPoly(img,[np.array(poly, np.int32)],(255,255,255))
    
    def mask_none(self):
        self.mask = 255 * np.ones((self.parameters['crop_box'][1][1] - self.parameters['crop_box'][0][1],
                                   self.parameters['crop_box'][1][0] - self.parameters['crop_box'][0][0]),
                                  dtype=np.uint8)
        if 'mask_ellipse' in self.parameters['crop_method']:
            self.parameters['mask_ellipse'] = None
        elif 'mask_polygon' in self.parameters['crop_method']:
            self.parameters['mask_polygon'] = None

    def apply_mask(self,frame):
        return cv2.bitwise_and(frame, self.mask)

    def apply_crop(self, frame):
        if np.size(np.shape(frame)) == 3:
            frame=frame[self.parameters['crop_box'][0][1]:self.parameters['crop_box'][1][1],
                self.parameters['crop_box'][0][0]: self.parameters['crop_box'][1][0],:]
        else:
            frame=frame[self.parameters['crop_box'][0][1]:self.parameters['crop_box'][1][1],
                self.parameters['crop_box'][0][0]: self.parameters['crop_box'][1][0]]
        return frame

    #def read_frame(self, n=None):
    #    frame = super().read_frame(n=n)
    #    
    #    return frame







