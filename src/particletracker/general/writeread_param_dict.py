def write_paramdict_file(params, filename):
    with open(filename.replace('*',''), 'w') as f:
        print(params, file=f)

def read_paramdict_file(filename):
    with open(filename.replace('*',''), 'r') as f:
        content = f.read()
        return eval(content)

