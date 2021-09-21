from ..customexceptions import AnnotatorError

class TextLabelError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'text_label error'
        self.e=e

class VarLabelError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'var_label error - Check var_column indicates column with data. Add data with postprocessing_method add_frame_data'
        self.e=e

class ParticleLabelsError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'particle_labels error'
        self.e=e

class GetClassSubsetError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'get_class_subset error'
        self.e=e

class CmapError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'Colour map error'
        self.e=e

class CirclesError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'circles error'
        self.e=e

class BoxesError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'boxes error - requires boxes to be run in postprocessing'
        self.e=e

class ContourInsideImageError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'contours inside image error'
        self.e=e

class ContoursError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'contours error - only works if using contours tracking method'
        self.e=e

class VoronoiError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        
        self.error_msg = 'voronoi error - requires voronoi to be run in postprocessing'
        self.e=e

class NetworksError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'networks error - requires neighbours to be run in postprocessing'
        self.e=e

class VectorsError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'vectors error'
        self.e=e

class VectorsError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'vectors error'
        self.e=e

class TrajectoriesError(AnnotatorError):
    def __init__(self,e):
        super().__init__(e)
        self.error_msg = 'tracjectories error - requires processed video and use_part_processed selected to work'
        self.e=e        
