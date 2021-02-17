from filehandling import get_directory_filenames, smart_number_sort
import os
import cv2
import numpy as np

class ImageReader():
    def __init__(self, filename=None, grayscale=False, frame_range=(0,None,1)):
        dirname = os.path.dirname(filename)
        self.file_extension = filename.split('.')[1]
        self.filefilter = dirname + '\*.' + self.file_extension
        self.init_video()
        

    def init_video(self):
        self.current=0
        self._filenames =  get_directory_filenames(self.filefilter, smart_sort=smart_number_sort, reverse_sort=False)
        self.get_vid_props()
    
    def get_vid_props(self):
        self.frame_num = self.current
        self.num_frames = len(self._filenames)
        self.current_time = None
        frame = cv2.imread(self._filenames[0])
        size = np.shape(frame)
        self.width = size[1]
        self.height = size[0]
        if np.size(size) == 3:
            self.colour = 3
            self.frame_size = (self.height, self.width, 3)
        else:
            self.colour = 1
            self.frame_size = (self.width, self.height)
        self.fps = None
        self.format = None
        self.codec = None
        

        self.properties = { 'frame_num' : self.frame_num,
            'num_frames' : self.num_frames,
            'width' : self.width,
            'height':self.height,
            'colour' : self.colour,
            'frame_size' : self.frame_size,
            'fps':self.fps,
            'codec':self.codec,
            'format':self.format,
            'file_extension':self.file_extension}

    def read_frame(self, n=None):
        if n is None:
            self.read_next_frame()
        elif (n >= 0) & (n < self.num_frames):
            self.current=n
            return cv2.imread(self._filenames[n])
        else:
            print('Requested frame not possible')

    def set_frame(self, n):
        if (n >= 0) & (n < self.num_frames):
            self.current = n
        else:
            print('Requested frame not possible')

    def read_next_frame(self):
        frame = cv2.imread(self._filenames[self.current])
        self.current = self.current + 1
        return frame

    def close(self):
        pass

    def __getitem__(self, frame_num):
        """Getter reads frame specified by passed index"""
        return self.read_frame(n=frame_num)

    def __len__(self):
        return self.num_frames

    def __iter__(self):
        return self

    def __next__(self):
        """
        Generator returns next available frame specified by step
        :return:
        """
        if self.frame_num < self.frame_range[1]:
            return self.read_frame()
        else:
            raise StopIteration

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


