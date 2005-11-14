from logilab.common.testlib import main
from solipsis.services.profile.tools.prefs import get_prefs, set_prefs

if __name__ == '__main__':
    import sys, os
    logging = get_prefs("log")
    if not logging:
        print "desactivating log"
    set_prefs("log", False)
    main(os.path.dirname(sys.argv[0]) or '.')
    set_prefs("log", logging)
