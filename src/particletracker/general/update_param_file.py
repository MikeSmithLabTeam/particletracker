from .writeread_param_dict import read_paramdict_file, write_paramdict_file


filename = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\1h_tl_range.param"


params = read_paramdict_file(filename)


params['postprocess']['find_tj_gb_coords'] = {
            'dilate_rad': [5,1,50,1],
        }

params['postprocess']['crystal_id'] = {
                        'peak_height': [30,1,60, 1],
                      'smoothing': [2.0,0.2,10.0,0.1],
                      'debug': [False, ('True', 'False')],
                      'shift': [0.0,-1.0, 1.0, 0.1],}

write_paramdict_file(params, filename)