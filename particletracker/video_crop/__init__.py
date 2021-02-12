import numpy as np
import cv2


#from .crop_methods import crop_box
from labvision.video import ReadVideo
from labvision.images import display

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
        if self.parameters['crop_box'] is not None:
            crop_height = self.parameters['crop_box'][1][1] - self.parameters['crop_box'][1][0]
            crop_width = self.parameters['crop_box'][0][1] - self.parameters['crop_box'][0][0]
            if (self.height != crop_height) or (self.width != crop_width):
                self.reset_mask()
        self.set_mask()   

    def reset_mask(self):
        #To set crop back to max image size
        self.parameters['crop_box']=None#((0, 0),(self.width, self.height))
        self.mask_none()
        
    def mask_none(self):
        self.mask = 255 * np.ones((self.height, self.width),
                                  dtype=np.uint8)
        for method in self.parameters['crop_method']:
            if 'crop' not in method:
                self.parameters[method]=None
    
    def create_empty_mask(self):
        #calculate mask given ellipse pts
        if self.parameters['crop_box'] is None:
            img = np.zeros((self.height,self.width), dtype=np.uint8)    
        else:
           img = np.zeros((self.parameters['crop_box'][1][1] - self.parameters['crop_box'][0][1],
                                   self.parameters['crop_box'][1][0] - self.parameters['crop_box'][0][0]),
                                  dtype=np.uint8)
        return img

    def set_mask(self):
        if self.parameters['crop_box'] is None:
            img = 255 * np.ones((self.height, self.width), dtype=np.uint8)
        else:
            img = 255 * np.ones((self.parameters['crop_box'][1][1] - self.parameters['crop_box'][0][1],
                                   self.parameters['crop_box'][1][0] - self.parameters['crop_box'][0][0]),
                                  dtype=np.uint8)
        self.mask = img.copy()
        for method in self.parameters['crop_method']:
            if 'crop' not in method:
                points = self.parameters[method]
                if points is None:
                    pass
                else:
                    if 'mask_ellipse' in method: 
                        mask = self.mask_ellipse(points)
                    elif 'mask_polygon' in method:
                        mask = self.mask_polygon(points)
                    elif 'mask_rect' in method:
                        mask = self.mask_rect(points)
                    elif 'mask_circle' in method:
                        mask = self.mask_circle(points)
                
                    if 'invert' in method:
                        self.mask = cv2.add(self.mask, mask)
                    else:
                        inverted_img = cv2.subtract(img, mask)
                        self.mask = cv2.subtract(self.mask, inverted_img)
                    
    def mask_ellipse(self, pts):
        img = self.create_empty_mask()
        if pts is None:
            mask = img
        else:
            ellipse = np.array([[pts[0][0],pts[0][1]],[pts[0][0],pts[1][1]],[pts[1][0],pts[1][1]],[pts[1][0],pts[0][1]]])
            rect=cv2.minAreaRect(ellipse)
            mask = cv2.ellipse(img,rect,255,thickness=-1)
        return mask

    def mask_polygon(self, pt_list):
        img = self.create_empty_mask()

        #calculate mask given points
        if pt_list is None:
            mask=img
        else:
            poly = []
            for point in pt_list:
                poly.append([point[0],point[1]])
            mask = cv2.fillPoly(img,[np.array(poly, np.int32)],(255,255,255))
        return mask
    
    def mask_circle(self, pts):
        img = self.create_empty_mask()

        if pts is None:
            mask = img
        else:            
            radius = ((pts[1][1]-pts[0][1])**2+(pts[1][0]-pts[0][0])**2)**0.5
            mask = cv2.circle(img,pts[0],int(radius),255,thickness=-1)
        return mask

    def mask_rect(self, pts):
        img = self.create_empty_mask()

        if pts is None:
            mask = img
        else:
            mask = cv2.rectangle(img, pts[0], pts[1], 255, thickness=-1)
        return mask

    def apply_mask(self,frame):
        print(np.shape(frame))
        print(np.shape(self.mask))
        return cv2.bitwise_and(frame, self.mask)

    def apply_crop(self, frame):
        if np.size(np.shape(frame)) == 3:
            if self.parameters['crop_box'] is not None:
                frame=frame[self.parameters['crop_box'][0][1]:self.parameters['crop_box'][1][1],
                        self.parameters['crop_box'][0][0]: self.parameters['crop_box'][1][0],:]
        else:
            if self.parameters['crop_box'] is not None:
                frame=frame[self.parameters['crop_box'][0][1]:self.parameters['crop_box'][1][1],
                        self.parameters['crop_box'][0][0]: self.parameters['crop_box'][1][0]]
        return frame







