import numpy as np
import cv2

from labvision.video import ReadVideo
from ..customexceptions import error_return_frame,  error_handling#flash_error_msg, CropMaskError,

class ReadCropVideo(ReadVideo):

    def __init__(self, parameters=None, filename=None, frame_range=(0,None,1), error_reporting=None):
        if error_reporting is not None:
            self.error = error_reporting
        try:
            ReadVideo.__init__(self, filename=filename, frame_range=parameters['config']['_frame_range'])
        except:
            #Avoid crash if new video has num_frames < max_frames in settings file.
            parameters['config']['_frame_range'] = (0, None, 1)
            ReadVideo.__init__(self, filename=filename, frame_range=parameters['config']['_frame_range'])

        self.parameters = parameters['crop']
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
            if (self.height < crop_height) or (self.width < crop_width):
                self.reset()
            self.crop_frame_size = (crop_width, crop_height)
        
        #If self.reset() called you could enter both if statements
        if self.parameters['crop_box'] is None:
            self.crop_frame_size = self.frame_size
        self.properties['crop_frame_size'] = self.crop_frame_size
        
        self.set_mask()
           
    def reset(self):
        #To set crop back to max image size
        self.parameters['crop_box']=None
        self.reset_mask()
        
        
    def reset_mask(self):
        #None for a mask means same size as crop.
        self.mask = self._create_ones_mask()

        for method in self.parameters['crop_method']:
            if 'crop' not in method:
                self.parameters[method]=None
    
    def _create_zeros_mask(self):
        if self.parameters['crop_box'] is None:
            img = np.zeros((self.height,self.width), dtype=np.uint8)    
        else:
           img = np.zeros((self.parameters['crop_box'][1][1] - self.parameters['crop_box'][0][1],
                                   self.parameters['crop_box'][1][0] - self.parameters['crop_box'][0][0]),
                                  dtype=np.uint8)
        return img
    
    def _create_ones_mask(self):
        if self.parameters['crop_box'] is None:
            img = 255*np.ones((self.height,self.width), dtype=np.uint8)    
        else:
           img = 255*np.ones((self.parameters['crop_box'][1][1] - self.parameters['crop_box'][0][1],
                                   self.parameters['crop_box'][1][0] - self.parameters['crop_box'][0][0]),
                                  dtype=np.uint8)
        return img

    def set_mask(self):
        img = self._create_zeros_mask()
        self.mask = img.copy()
        
        no_mask = True
        for method in self.parameters['crop_method']:
            if 'crop' not in method:
                points = self.parameters[method]
                if points is not None:
                    no_mask=False
                    if 'mask_ellipse' in method: 
                        mask = self.mask_ellipse(points)
                    elif 'mask_polygon' in method:
                        mask = self.mask_polygon(points)
                    elif 'mask_rect' in method:
                        mask = self.mask_rect(points)
                    elif 'mask_circle' in method:
                        mask = self.mask_circle(points)
                    
                    #img = cv2.subtract(img, mask)
                    self.mask = cv2.add(self.mask, mask)
        if no_mask:
            self.mask = self._create_ones_mask()
                    
    def mask_ellipse(self, pts):
        img = self._create_zeros_mask()
        if pts is None:
            mask = img
        else:
            ellipse = np.array([[pts[0][0],pts[0][1]],[pts[0][0],pts[1][1]],[pts[1][0],pts[1][1]],[pts[1][0],pts[0][1]]])
            rect=cv2.minAreaRect(ellipse)
            mask = cv2.ellipse(img,rect,255,thickness=-1)
        return mask

    def mask_polygon(self, pt_list):
        img = self._create_zeros_mask()

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
        img = self._create_zeros_mask()

        if pts is None:
            mask = img
        else:            
            radius = int(((pts[1][1]-pts[0][1])**2+(pts[1][0]-pts[0][0])**2)**0.5)
            # Convert center point coordinates to integers
            center = (int(pts[0][0]), int(pts[0][1]))
            mask = cv2.circle(img, center, int(radius), 255, thickness=-1)
        return mask

    def mask_rect(self, pts):
        img = self._create_zeros_mask()

        if pts is None:
            mask = img
        else:
            mask = cv2.rectangle(img, pts[0], pts[1], 255, thickness=-1)
        return mask

    @error_return_frame
    def apply_mask(self,frame):
        return cv2.bitwise_and(frame, self.mask)        
    
    @error_return_frame
    def apply_crop(self, frame):
        return crop(frame, self.parameters)

    def read_frame(self, n=None):
        frame=super().read_frame(n=n)
        cropped_frame=self.apply_crop(frame)
        return cropped_frame
    

def crop(frame, parameters):
    if np.size(np.shape(frame)) == 3:
            if parameters['crop_box'] is not None:
                frame=frame[parameters['crop_box'][0][1]:parameters['crop_box'][1][1],
                        parameters['crop_box'][0][0]: parameters['crop_box'][1][0],:]
    else:
        if parameters['crop_box'] is not None:
            frame=frame[parameters['crop_box'][0][1]:parameters['crop_box'][1][1],
                    parameters['crop_box'][0][0]: parameters['crop_box'][1][0]]
    return frame

