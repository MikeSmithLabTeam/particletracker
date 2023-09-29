def write_paramdict_file(params, filename):
    with open(filename, 'w') as f:
        print(params, file=f)

def read_paramdict_file(filename):
    print('test', filename)
    with open(filename, 'r') as f:
        content = f.read()
        return eval(content)

