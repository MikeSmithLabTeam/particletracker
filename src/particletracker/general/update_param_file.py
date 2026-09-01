from .writeread_param_dict import read_paramdict_file, write_paramdict_file


filename = "/home/mike/Documents/scalebar.param"


params = read_paramdict_file(filename)


params['postprocess']['find_tj_gb_coords'] = {
            'dilate_rad': [5,1,50,1],
        }

params['annotate']['plot_tj_gb'] = {
            'tj_colour':(200, 200, 200),
            'tj_radius':5,
            'tj_thickness':2,            
            'gb1_colour':(0, 255, 255),
            'gb2_colour':(255, 255, 0),
            'gb3_colour':(255, 0, 255),
            'gb_thickness':2,
        }

write_paramdict_file(params, filename)