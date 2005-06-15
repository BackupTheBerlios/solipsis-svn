#!/usr/bin/env python

import os
import os.path
import sys

if __name__ == '__main__':
    # Adjust path
    current_file = sys.argv[0]
    current_path = os.path.normcase(os.path.dirname(os.path.abspath(current_file)))
    os.chdir(current_path)
    if not current_path in sys.path:
        sys.path.insert(0, current_path)
    # Launch
    from solipsis.node import main
    main.main()
