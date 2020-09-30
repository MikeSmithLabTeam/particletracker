from ParticleTrackingSimple.general.imageformat import bgr_2_grayscale
from ParticleTrackingSimple.video_crop.crop_methods import crop_box
from labvision.video import ReadVideo
from labvision.images.basics import display
from labvision.images.cropping import mask
import numpy as np
import cv2

class ReadCropVideo(ReadVideo):

    def __init__(self, parameters=None, filename=None, frame_range=(0,None,1)):
        ReadVideo.__init__(self, filename=filename, frame_range=frame_range)
        self.parameters = parameters
        self.crop_vals = parameters['crop_box']
        '''
        If loading a new video with different dimensions,
        then the stored crop and mask parameters may not fit.
        Perform a check. If fails reset crop and mask to frame
        dimensions. This may not sort the gui but it will stop
        a crash.
        '''
        crop_height = self.crop_vals[1][1] - self.crop_vals[1][0]
        crop_width = self.crop_vals[0][1] - self.crop_vals[0][0]
        if (self.height < crop_height) or (self.width < crop_width):
            self.reset_crop()

        self.set_crop(self.crop_vals)

        if 'mask_ellipse' in parameters['crop_method']:
            ellipse_pts = parameters['mask_ellipse']
            self.mask_ellipse(ellipse_pts)
        elif 'mask_polygon' in parameters['crop_method']:
            points = parameters['mask_polygon']
            self.mask_polygon(points)
        else:
            self.mask_none()

    def set_crop(self, crop_coords):
        #Crops image to size specified by crop_coords and sets mask to None.
        self.crop_vals = crop_coords

    def mask_none(self):
        self.mask = 255 * np.ones((self.crop_vals[1][1] - self.crop_vals[1][0], self.crop_vals[0][1] - self.crop_vals[0][0]),
                                  dtype=np.uint8)
        if 'mask_ellipse' in self.parameters['crop_method']:
            self.parameters['mask_ellipse'] = None
        elif 'mask_polygon' in self.parameters['crop_method']:
            self.parameters['mask_polygon'] = None

    def reset_crop(self):
        #To set crop back to max image size
        self.set_crop(((0, self.width),(0, self.height)))
        self.mask_none()

    def mask_ellipse(self, ellipse_pts):
        #calculate mask given ellipse pts
        if ellipse_pts is None:
            self.mask_none()
            return self.mask
        else:
            self.mask_none()
            img=~self.mask
            pts = ellipse_pts
            ellipse = np.array([[pts[0][0],pts[0][1]],[pts[0][0],pts[1][1]],[pts[1][0],pts[1][1]],[pts[1][0],pts[0][1]]])
            rect=cv2.minAreaRect(ellipse)
            ellipse_mask = cv2.ellipse(img,rect,255,thickness=-1)
            self.mask = ellipse_mask
            self.parameters['mask_ellipse'] = ellipse_pts
            return self.mask

    def mask_polygon(self, point_list):
        #calculate mask given points
        if point_list is None:
            self.mask_none()
            return self.mask
        else:
            self.mask_none()
            img=~self.mask
            poly = []
            for point in point_list:
                poly.append([point[0],point[1]])
            self.mask = cv2.fillPoly(img,[np.array(poly, np.int32)],(255,255,255))
            self.parameters['mask_polygon'] = point_list
            return self.mask

    def apply_mask(self,img):
        return cv2.bitwise_and(img, self.mask)

    def read_frame(self, n=None):
        frame = super().read_frame(n=n)
        frame = frame[self.crop_vals[1][0]:self.crop_vals[1][1], self.crop_vals[0][0]: self.crop_vals[0][1],:]
        return frame







