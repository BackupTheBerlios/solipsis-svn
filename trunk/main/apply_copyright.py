#!/usr/bin/python

import os
import sys
import re


def comment_copyright(copyright):
    sys.stdout.write('# <copyright>\n')
    lines = list(copyright)
    # Strip leading and tailing empty lines
    begin = 0
    end = len(lines)
    while not lines[end-1].strip():
        last -= 1
    while not lines[begin].strip():
        begin += 1
    for l in lines[begin:end]:
        sys.stdout.write('# ' + l)
    sys.stdout.write('# </copyright>\n')

def strip_copyright(f):
    start_regex = re.compile(r'^#\s*<copyright>\s*$')
    end_regex = re.compile(r'^#\s*</copyright>\s*$')
    filtered = False
    junk = []
    for l in f:
        if not filtered:
            if start_regex.match(l.strip()):
                filtered = True
            else:
                yield l
        if filtered:
            junk.append(l)
            if end_regex.match(l.strip()):
                filtered = False
    if filtered:
        for l in junk:
            yield l

def main():
    f = sys.stdin
    remains = list(strip_copyright(f))
    f.close()
    comment_copyright(file('COPYRIGHT'))
    for l in remains:
        sys.stdout.write(l)

if __name__ == '__main__':
    main()
