def write_paramdict_file(params, filename):
    with open(filename, 'w') as f:
        print(params, file=f)

def read_paramdict_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
        return eval(content)


if __name__ == '__main__':
    filename = '/home/mike/PycharmProjects/ParticleTrackingSimple/project/param_files/test.param'

    a = {'c':1,'d':2}
    b = {'d':1,'e':2}
    params = {'a':a,'b':b}

    write_paramdict_file(params, filename)
    params2 = read_paramdict_file(filename)

    print(params2['a'])