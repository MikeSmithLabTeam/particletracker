from ..customexceptions import PostprocessorError

class AngleError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'angle error'
        self.e = e

class ContourAreaError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'contour area error'
        self.e = e

class ContourBoxesError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'contour boxes error - works only with contours method'
        self.e = e

class DifferenceError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'difference error - requires preprocessed dataframe and select use_part_processed'
        self.e = e

class MagnitudeError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'magnitude error'
        self.e = e

class MaxError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'max error'
        self.e = e

class MeanError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'mean error  -  Check that you are operating on multiframe data. Have you "processed part"? Is the use-part button checked?'
        self.e = e

class MedianError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'median error'
        self.e = e

class MinError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'min error'
        self.e = e

class RateError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'rate error - requires preprocessed dataframe and select use_part_processed'
        self.e = e

class ClassifyError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'classify error'
        self.e = e

class LogicNotError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'logic_NOT error'
        self.e = e

class LogicAndError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'logic_AND error'
        self.e = e

class LogicOrError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'logic_OR error'
        self.e = e

class AddFrameDataError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'add_frame_data error - file type should be Csv with single column of data of same length as number of frames'
        self.e = e

class NeighboursError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'neighbours error'
        self.e = e

class VoronoiError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'voronoi error'
        self.e = e

class HexaticOrderError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'hexatic error'
        self.e = e

class RealImagError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'real_imag error - Check you are working with a complex number in the input column'
        self.e = e

class AbsoluteError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = 'absolute error'
        self.e = e


class RemoveMaskedError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = "remove masked objects error"

class AudioFrequencyError(PostprocessorError):
    def __init__(self, e):
        super().__init__(e)
        self.error_msg = "Audio frequency error, ffmpeg must be installed on system"
