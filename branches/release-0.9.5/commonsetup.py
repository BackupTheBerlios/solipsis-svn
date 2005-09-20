
import os
import glob

def get_dynamic_modules():
    """
    Returns dynamic modules to be bundled by default.
    """
    print "enumerating dynamic modules"
    includes = []

    service_dir = 'solipsis/services'
    # 1. Dynamically-loaded service plugins
    for filename in os.listdir(service_dir):
        path = os.path.join(service_dir, filename)
        if os.path.isdir(path) and not filename.startswith('_') and not filename.startswith('.'):
            package = path.replace('/', '.')
    #         packages.append(package)
            includes.append(package + '.plugin')

    extension_dirs = ['solipsis/node/discovery', 'solipsis/node/controller', 'solipsis/lib/shtoom']
    # 2. Dynamically-loaded behaviour extensions
    for dir in extension_dirs:
        for path in glob.glob(os.path.join(dir, '*.py')):
            filename = os.path.basename(path)
            if not filename.startswith('_'):
                module = path.replace('/', '.')[:-3]
                includes.append(module)

#     print "includes =", includes
    return includes

def get_data_files():
    """
    Returns all resource files and dirs.
    """
    print "enumerating resources"
    data_files = []

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
        if dirpath.startswith('./dist/') or dirpath.startswith('./build/') or '/.svn' in dirpath:
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
        data_files.append((dirpath, files))

#     print "data_files =", data_files
    return data_files
