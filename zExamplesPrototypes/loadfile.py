import os, sys, sysconfig
import pickle, json


fin = open("trace.bin", 'rb')
fout = open("trace.txt", "w")

project_path = sys.path[0]
paths_dict = sysconfig.get_paths()
site_pkgs = paths_dict['purelib']
stdlib = paths_dict['stdlib']


def get_file_string(path):
    if site_pkgs in path:
        return path.replace(f"{site_pkgs}{os.sep}", "pip: ")
    elif project_path in path: 
        return path.replace(f"{project_path}{os.sep}", "OUR: ")
    elif stdlib in path: 
        return path.replace(f"{stdlib}{os.sep}", "builtin: ")
    else:
        return path


counts, calledfuncs, callers = pickle.load(fin)

for i, item in enumerate(callers.items()):
    k, v = item
    out = ''
    parent, child = k
    source, module, func = parent
    out += f'"{get_file_string(source)},\\n{func}"->'
    source, module, func = child
    out += f'"{get_file_string(source)},\\n{func}" [label="{i}"];\n\n'
    fout.write(out)

fin.close()
fout.close()
