from ..customexceptions import TrackError

class TrackpyError(TrackError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'trackpy error'
        self.e=e

class ContoursError(TrackError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'contours error'
        self.e=e

class BoxesError(TrackError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'boxes error'
        self.e=e

class HoughCirclesError(TrackError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'hough circles error'
        self.e=e