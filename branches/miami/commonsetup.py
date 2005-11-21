
import os
import glob
import sys
import re


def create_dyn_file(template, var_replace=None):
    """
    Dynamically creates file from template.
    (in 'dyn' directory).
    """
    dyndir = "dyn"
    template = os.path.join(dyndir, template)
    dynfile = template.replace('.tmpl.py', '.py')
    print "generating %s" % dynfile

    if var_replace is None:
        var_replace = {}

    f = file(template, 'r')
    s = f.read()
    f.close()
    for k, v in var_replace.items():
        s, n = re.subn(r'[^\r\n]+#\s*<%s>([\r\n])' % k, "%s = %s\n\\1" % (k, repr(v)), s)
        if n == 0:
            print "Couldn't find var '%s' in template '%s'. Bailing out." % (k, template)
            sys.exit(1)

    f = file(dynfile, 'w')
    f.write(s)
    f.close()


def get_dynamic_modules():
    """
    Returns dynamic modules to be bundled by default.
    """
    print "enumerating dynamic modules"
    includes = []
    sep = os.sep

    service_dir = 'solipsis/services'
    service_dir = os.path.normpath(service_dir)
    # 1. Dynamically-loaded service plugins
    for filename in os.listdir(service_dir):
        path = os.path.join(service_dir, filename)
        if os.path.isdir(path) and not filename.startswith('_') and not filename.startswith('.'):
            package = path.replace(sep, '.')
    #         packages.append(package)
            includes.append(package + '.plugin')

    extension_dirs = ['solipsis/node/discovery', 'solipsis/node/controller', 'solipsis/lib/shtoom']
    # 2. Dynamically-loaded behaviour extensions
    for dir_ in extension_dirs:
        dir_ = os.path.normpath(dir_)
        for path in glob.glob(os.path.join(dir_, '*.py')):
            filename = os.path.basename(path)
            if not filename.startswith('_'):
                module = path.replace(sep, '.')[:-3]
                includes.append(module)

#     print "includes =", includes
    return includes

def get_data_files(other_data_files=None):
    """
    Returns all resource files and dirs.
    """
    print "enumerating resources"
    sep = os.sep
    dir_files = {}
    if other_data_files:
        for dirpath, files in other_data_files:
            try:
                l = dir_files[dirpath]
            except KeyError:
                l = []
                dir_files[dirpath] = l
            l.extend(files)

    # Please note: base directories of service plugins will be automatically
    # included as long as they contain some localization data (.mo files)
    extensions = [
        'xrc',
        'mo',
        'png', 'gif', 'jpg', 'jpeg',
        'txt', 'html',
        'conf', 'default',
    ]
    for dirpath, dirnames, filenames in os.walk('.'):
        if dirpath.startswith('.' + sep + 'dist' + sep) or \
            dirpath.startswith('.' + sep + 'build' + sep) or \
            (sep + '.svn') in dirpath:
            continue
        found = False
        files = []
        dirpath = dirpath[2:]
        # Include files with one of the registered extensions
        for filename in filenames:
            for ext in extensions:
                if filename.endswith('.' + ext):
                    break
            else:
                continue
            path = os.path.join(dirpath, filename)
            files.append(path)
            found = True
        try:
            l = dir_files[dirpath]
        except KeyError:
            l = []
            dir_files[dirpath] = l
        l.extend(files)

    data_files = dir_files.items()
    data_files.sort()
#     print "data_files =", data_files
    return data_files
