from .writeread_param_dict import write_paramdict_file

def create_param_file(filename):
    experiment = {'experiment_method':('video_filename','sample', 'fps'),
                  'video_filename':None,
                  'sample':'Sample',
                  'fps':30,
                  'metadata':None,
                  'frame_range':(0,None,1)
                  }

    crop = {'crop_method': ('crop_box',),
            'crop_box':None,
            'mask_ellipse': None,
            'mask_circle': None,
            'mask_polygon': None,
            'mask_rectangle': None,
            }

    preprocess = {
        'preprocess_method': ('grayscale','medianblur',),
        'grayscale':{},#'load_bkg_img':False,
        'threshold':{'threshold':[1,0,255,1],
                     'th_mode':[True,('True', 'False')]},
        'adaptive_threshold':{'block_size': [29,1,300,2],
                              'C': [-23, -30, 30, 1],
                              'ad_mode': [True, ('True', 'False')]
                              },
        'colour_channel':{'colour':['red',('red','green','blue')]},
        'distance':{},
        'blur':{'kernel':[1,1,15,2]},
        'medianblur':{'kernel':[3,1,15,2]},
        'gamma':{'gamma':[1.00,0.01,10.00,0.01]},
        'subtract_bkg':{'subtract_bkg_type':['mean',('mean','median','grayscale','red','green','blue')],
                    'subtract_bkg_filename':None,
                    'subtract_bkg_blur_kernel': [3,1,15,2],
                    'subtract_bkg_invert':[True,('True','False')],
                    'subtract_bkg_norm':[True,('True','False')]
                    },
        'absolute_diff':{'normalise':[True,('True','False')],
                    'value':[125,1,255,1]
                    },
        'fill_holes':{},
        'invert':{},
        'erosion':{'erosion_kernel':[1,1,11,2],
                    'iterations':[1,1,11,1]
                    },
        'dilation':{'dilation_kernel':[1,1,11,2],
                    'iterations':[1,1,11,1]
                    }
        }

    track = {
        'track_method':('contours',),
        'trackpy':{'diameter':[7,1, 101,2],
                   'percentile': [64, 0, 100, 1],
                   'minmass': [100.0, 0.0, 1000.0, 0.1],
                   'max_iterations': [10, 1, 50, 1],
                   'invert':[False, ('True','False')],
                   'get_intensities':False,
                   'intensity_radius':[2,1,200,1]                   
                   },
        'hough':{'min_dist':[105,1,501,2],
                  'p1':[75, 1, 201,2],
                  'p2':[39, 1, 201,2],
                  'min_rad':[10, 1, 301,2],
                  'max_rad':[50, 1, 301,2],
                  'get_intensities':False
                 },
        'contours':{'noise_cutoff':[2,1,50,1],
                    'area_min':[20, 1, 2000, 1],
                    'area_max':[2000, 1, 20000, 1],
                    'aspect_min':[1.0,1.0,10.0,0.1],
                    'aspect_max':[10.0,1.0,10.0,0.1],
                    'get_intensities':False
                    },
        }

    link = {
        'link_method':('default',),
        'default':{ 'max_frame_displacement': [10,1,50,1],
                    'memory': [3,0,30,1],
                    'min_frame_life': [10,1,100,1]
                    }
        }

    postprocess = {
        'postprocess_method': (),
        'angle':{'x_column':'x',
                 'y_column':'y',
                 'output_name':'theta',
                 'units':['degrees',('radians','degrees')]},
        'audio_frequency':{},
        'classify':{'column_name':'x',
                    'output_name':'classifier',
                    'lower_threshold':[0.01, 0.01, 100.00, 0.01],
                    'upper_threshold':[100.00, 1.00, 2000.00, 0.01]
                    },
        'contour_boxes':{},
        'logic_AND':{'column_name':'classifier1',
                     'column_name2':'classifier2',
                     'output_name':'classifier'},
        'logic_OR': {'column_name': 'classifier1',
                      'column_name2': 'classifier2',
                      'output_name': 'classifier'},
        'logic_NOT': {'column_name': 'classifier',
                      'output_name': 'classifier1'},
        'magnitude':{'column_name':'x_diff',
                     'column_name2':'y_diff',
                     'output_name':'r_diff'},
        'neighbours':{'method':['delaunay',('delaunay','kdtree')],
                      'neighbours':6,
                      'cutoff':[50,1,200,1],
                    },
        'voronoi':{},
        'difference':{'column_name':'x',
                      'output_name':'x_diff',
                      'span':[10,1,50,1]
                      },

        'median':{'column_name':'r_diff',
                    'output_name':'median_r',
                    'span':[5,1,20,1]},
        'mean':{'column_name':'x',
                'output_name':'x_mean',
                'span':[5,1,20,1]
                },
        'rate':{'column_name':'x',
                'output_name':'vx',
                'fps':50.0,
                'span':[5,1,20,1]
                  },
        'remove_masked':{},
        'add_frame_data':{
            'new_column_name':'data',
            'data_filename':None
                  },
        'hexatic_order':{
            'threshold': [10, 1, 100, 1]
        }

        }

    annotate = {
        'annotate_method': ('circles',),
        'text_label':{'text':'BP1',
                     'position':(100,100),
                     'font_colour':(255,0,0),
                     'font_size':3,
                     'font_thickness':2
                     },
        'var_label':{'var_column':'index',
                     'position':(100,100),
                     'font_colour':(255,0,255),
                     'font_size':4,
                     'font_thickness':3
                     },
        'particle_labels': {'values_column': 'particle',
                            'font_colour': (255, 0, 255),
                            'font_size': 1,
                            'font_thickness': 2
                            },
        'boxes':{'cmap_type':['static',('dynamic','static')],
                'cmap_column':'x',  #None
                'cmap_max':[100.0,0,1000.0,0.1],#For dynamic
                'cmap_min':[0.0,0.0,1000.0,0.1],
                'cmap_name': 'jet',
                'colour': (0, 255, 0),  # For static
                'classifier_column': None,  # For static or dynamic
                'classifier': [True, ('True','False')],
                'thickness': 2
                },
        'circles':{'xdata_column':'x',
                    'ydata_column':'y',
                    'rad_from_data':[False,('True','False')],
                    'rdata_column':'r',
                    'user_rad':[6,1,1000,1],
                    'cmap_type':['static',('dynamic','static')],
                    'cmap_column':'x',#for dynamic
                    'cmap_max':[100.0,0,1000.0,0.1],#For dynamic
                    'cmap_min':[0.0,0.0,2000.0,0.1],
                    'cmap_name': 'jet',
                    'colour': (0,255,0),#For static
                    'classifier_column': None,#For static or dynamic
                    'classifier': [True, ('True','False')],#For static or dynamic
                    'thickness':2
                   },
        'contours':{'cmap_type':['static',('dynamic','static')],
                    'cmap_column':'x',#For dynamic
                    'cmap_max':[100.0,0,1000.0,0.1],#For dynamic
                    'cmap_min':[0.0,0.0,1000.0,0.1],
                'cmap_name': 'jet',
                    'colour': (0,255,0),#For static
                    'classifier_column': None,#For static or dynamic
                    'classifier': [True, ('True','False')],
                    'thickness':2
                    },
        'trajectories':{'x_column':'x',
                    'y_column':'y',
                    'traj_length': [1000,0,1000,1],
                    'cmap_type':['static',('dynamic','static')],
                    'cmap_column':'x',#For dynamic
                    'cmap_max':[100.0,0,1000.0,0.1],#For dynamic
                    'cmap_min':[0.0,0.0,1000.0,0.1],
                'cmap_name': 'jet',
                    'colour': (64,224,208),#For static
                    'classifier_column':None,#For static or dynamic
                    'classifier': [True, ('True','False')],
                    'thickness':2
                   },
        'vectors':{ 'dx_column':'x',
                    'dy_column':'y',
                    'thickness':2,
                    'line_type':[8,('-1','4','8','16')],
                    'tip_length':[1,1,100,1],
                    'vector_scale':[1,1,2000,1],
                    'cmap_type':'static',#'dynamic',
                    'cmap_column':'x',#For dynamic
                    'cmap_max':[100.0,0,1000.0,0.1],#For dynamic
                    'cmap_min':[0.0,0.0,1000.0,0.1],
                'cmap_name': 'jet',
                    'colour': (0,0,255),#For static
                    'classifier_column':None,#For static or dynamic
                    'classifier': [True, ('True','False')],
                    'thickness':2
                    },
        'networks':{
                    'cmap_type':['static',('dynamic','static')],
                    'cmap_column':'x',#For dynamic                  
                    'cmap_max':[100.0,0,1000.0,0.1],#For dynamic
                    'cmap_min':[0.0,0.0,1000.0,0.1],
                'cmap_name': 'jet',
                    'classifier_column': None,
                    'classifier': [True, ('True','False')],
                    'colour': (0,255,0),#For static
                    'thickness':2
                    },
        'voronoi':{
                    'cmap_type':['static',('dynamic','static')],
                    'cmap_column':'voronoi_area',#For dynamic                      'classifier': 1,#For static or dynamic
                    'cmap_max':[100.0,0,1000.0,0.1],#For dynamic
                    'cmap_min':[0.0,0.0,1000.0,0.1],
                'cmap_name': 'jet',
                    'classifier_column': None,
                    'classifier': [True, ('True','False')],
                    'colour': (0,255,0),#For static
                    'thickness':2
                    },
        
        }

    selected = {'experiment':True,
                'crop':True,
                'preprocess':True,
                'track':True,
                'link':True,
                'postprocess':False,
                'annotate':False
                }

    PARAMETERS = {
        'experiment': experiment,
        'crop': crop,
        'preprocess':preprocess,
        'track':track,
        'link':link,
        'postprocess':postprocess,
        'annotate':annotate,
        'selected':selected
        }

    write_paramdict_file(PARAMETERS, filename)



