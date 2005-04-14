import re, sys

line1 = "FINDNEAResT SOLIPSIS/1.0"
line2 = "Position: 1235989454545 - 454578787888787876646"
line3 = "Remote-Address: 192.235.25.3:5678"
buffer = [line1, line2, line3]

rawData = "\r\n".join(buffer)
print rawData

data = rawData.splitlines()
p = re.compile(r'(\w+)\s+SOLIPSIS/(\d+\.\d+)')
m = p.match(data[0])

if m is None:
    print "no match"
    sys.exit(0)
method = m.group(1).upper()
version = m.group(2)

print "version:" + version
print "method:" + method

HEADERS_SYNTAX = {
    'Position': '^\s*\d+\s*-\s*\d+$',
    'Remote-Address':  '\s*.*:\d+\s*',
    'AwarenessRadius': '\d+',
    'Calibre': '\d+' }

ALL_HEADERS = ['Address', 'Id', 'Position', 'AwarenessRadius', 'Calibre',
               'Orientation', 'Pseudo']
ALL_REMOTE_HEADERS = [  'Remote-Address', 'Remote-Id', 'Remote-Position',
                        'Remote-AwarenessRadius', 'Remote-Calibre',
                        'Remote-Orientation', 'Remote-Pseudo']
METHODS = {
    'FINDNEAREST': ['Position', 'Id','Remote-Address'],
    'BEST' : ALL_HEADERS,
    'DETECT' : ALL_REMOTE_HEADERS }

if not METHODS.has_key(method):
    print "unknown method " + method
else:
    headers = METHODS[method]

print "possible headers:"
print headers    

p2 = re.compile(r'(\w+(?:-\w+)?)\s*:\s*(.*)')
for line in data[1:]:
    m2 = p2.match(line)
    if m2 is None:
        print "pattern does not match"
    headername = m2.group(1)
    headerval  = m2.group(2)
    if headername not in headers:
        print "unknown header %s for method %s" % (headername, method)
    else:
        headerPattern = re.compile(HEADERS_SYNTAX[headername])
        print "pattern used : " + HEADERS_SYNTAX[headername]
        m3 = headerPattern.match(headerval)
        if m3 is None:
            print "invalid syntax for header %s\n value given : %s" % (headername,
                                                                       headerval)
        else:
            print m3.group(0)
