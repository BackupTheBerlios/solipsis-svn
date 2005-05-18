import logilab.common.testlib as testlib

if __name__ == '__main__':
    import sys, os
    tests = testlib.find_tests(os.getcwd(), testlib.DEFAULT_PREFIXES, excludes=[])
    for test in tests:
        test_module = __import__(test)
        test_module.main()
