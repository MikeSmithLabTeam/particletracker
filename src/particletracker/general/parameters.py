import functools
import os

def get_param_val(param):
    '''
    Simple function to determine if parameter is a list or something else

    :param param: parameter to be tested
    :return: value from position zero of list or returns the parameter as is if not a list
    '''
    type_param = type(param)
    if type_param == type([]):
        return param[0]
    else:
        return param

def get_method_name(method):
    """get_method_name function. This function returns the method name and call number from the method string."""
    if '*' in method:
        method_name, call_num = method.split('*')
    else:
        method_name = method
        call_num = None
    return method_name, call_num

def get_method_key(method, call_num=None):
    """get_method_key function. This function returns the method key for the parameters dictionary. It checks if the method is called multiple times and if so, appends the call number to the method name."""
    if call_num is None:
        method_key = method
    else:
        method_key = method + '*' + call_num
    return method_key

def get_span(params):
    """params is a section of param dictionary e.g parameters['postprocess']"""
    span=1
    for key in params.keys():
        if type(params[key]) is dict:
            for key_inner in params[key].keys():
                if key_inner == 'span':
                    if params[key][key_inner][0] > span:
                        span = params[key][key_inner][0]
    return span

def get_parent(func):
    filename = func.__file__

def parse_values(sender, value):
    '''
    Determines the type of QWidget sending and converts data to
    correct format for entry into the parameters dictionary.
    A lot of this code is turning string representations into actual
    python data types.
    '''
    
    if sender.widget == 'slider':
        return [value, sender.slider._min, sender.slider._max, sender.slider._step]
    elif (sender.widget == 'textbox') or (sender.widget == 'dropdown'):
        if sender.widget == 'dropdown':
            value = sender.value_
        if value == ('None' or 'none'):
            return None
        elif value == ('True' or 'true'):
            return True
        elif value == ('False' or 'false'):
            return False
        elif (value == True) or (value == False) or (value is None):
            return value
        elif '((' in value:
            'Assumes nested tuples that look like ((1,2),(2,3),(4,5).....)'
            split_string = value[2:-2].replace(' ', '').split('),(')
            value = tuple([tuple(map(int,split_string[i].split(','))) for i in range(len(split_string))])
            return value
        elif '(' in value:
            #Creates a tuple of values from a string representing a tuple
            value = tuple(list(map(int, value[1:-1].replace(' ','').split(','))))
            return value
        else:
            return value
    else:
        #Purely future proofing
        print('Parsing of this widget type not implemented')
        return value

def ok_to_duplicate_method_check(method):
    not_to_be_duplicated = ['crop_box']
    return method not in not_to_be_duplicated


def param_parse(func):
    """param_format decorator. This performs steps to correctly format the parameters for the function call.
    
    When you call a function which has this decorator it extracts the method_key from the function name. It then extracts the 
    section of the parameters dictionary corresponding to that method_key. It parses the parameter values to form
    a dictionary which is then passed to the function as part of the kwargs. Only use this if you just
    need the section of the dictionary corresponding to the method_key. If you need other bits of the dictionary
    you'll need to implement this inside  your function and not have the decorator.

    There is an example in preprocessing >  subtract_bkg
    # """
    @functools.wraps(func)
    def wrapper_param_format(*args, **kwargs):
        method_key = get_method_key(func.__name__, call_num=kwargs['call_num'])
        params = kwargs['parameters'][kwargs['section']][method_key]
        params = {key : get_param_val(value) for (key, value) in params.items()}
        kwargs['parameters'] = params
        return func(*args, **kwargs)
    return wrapper_param_format
