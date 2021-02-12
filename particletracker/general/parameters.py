
def get_param_val(param):
    '''
    Simple function to determine if parameter is a list or something else
    Lists are 4 long and indicate an a parameter adjusted by the slider in TrackGui

    :param param: parameter to be tested
    :return: value from position zero of list or returns the parameter as is if not a list
    '''
    type_param = type(param)
    if type_param == type([]):
        return param[0]
    else:
        return param

def get_method_name(method):
    if '*' in method:
        method_name, call_num = method.split('*')
    else:
        method_name = method
        call_num = None
    return method_name, call_num

def get_method_key(method, call_num=None):
    if call_num is None:
        method_key = method
    else:
        method_key = method + '*' + call_num
    return method_key

def parse_values(sender, value):
    '''
    Determines the type of QWidget sending and converts data to
    correct format for entry into the parameters dictionary.
    '''
    if sender.widget == 'slider':
        return [value, sender.slider._min, sender.slider._max, sender.slider._step]
    elif sender.widget == 'textbox':
        if value == ('None' or 'none'):
            return None
        elif value == ('True' or 'true'):
            return True
        elif value == ('False' or 'false'):
            return False
        elif '((' in value:
            'Assumes nested tuples that look like ((1,2),(2,3),(4,5).....)'
            split_string = value[2:-2].replace(' ', '').split('),(')
            value = tuple([tuple(map(int,split_string[i].split(','))) for i in range(len(split_string))])
            return value
        elif '(' in value:
            return tuple(list(map(int, value[1:-1].replace(' ','').split(','))))
        else:
            return value
    else:
        #Purely future proofing
        print('Parsing of this widget type not implemented')
        return value

def ok_to_duplicate_method_check(method):
    not_to_be_duplicated = ['crop_box']
    return method not in not_to_be_duplicated
