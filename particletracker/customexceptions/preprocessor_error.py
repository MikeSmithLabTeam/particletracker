from ..customexceptions import PreprocessorError

class AdaptiveThresholdError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'adaptive_threshold error'
        self.e=e

class BlurError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'blur error - Check input is grayscale'
        self.e=e

class ColorChannelError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = "color channel error : valid options are 'red','green','blue'; requires a coloured image as input"
        self.e=e

class DilationError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'dilation error'
        self.e=e

class DistanceError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'distance error'
        self.e=e

class ErosionError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'erosion error'
        self.e=e

class GammaError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'gamma error'
        self.e=e

class GrayscaleError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'grayscale error'
        self.e=e

class InvertError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'invert error'
        self.e=e

class MedianBlurError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'median_blur error'
        self.e=e

class SubtractBkgError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'subtract_bkg error'
        self.e=e

class ThresholdError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'threshold error'
        self.e=e

class VarianceError(PreprocessorError):
    def __init__(self,e):
        super().__init__()
        self.error_msg = 'variance error'
        self.e=e






