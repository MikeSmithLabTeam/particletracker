from ..customexceptions import TrackError

class TrackpyError(TrackError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'trackpy error'
        self.e=e

class ContoursError(TrackError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'contours error'
        self.e=e

class HoughCirclesError(TrackError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'hough circles error'
        self.e=e


class RemoveMaskedError(TrackError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = "remove masked objects error"

"""--------------------------------------------------------------------------------------
These exceptions are associated with the get_intensities methods
-------------------------------------------------------------------------------------------
"""

class MeanIntensityError(TrackError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'When using get_intensities.mean_intensity there was an error'
        self.e=e

class RedBlueError(TrackError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'When using get_intensities.red_blue there was an error'
        self.e=e