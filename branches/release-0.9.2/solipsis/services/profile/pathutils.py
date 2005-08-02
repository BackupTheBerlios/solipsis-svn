# 2005/06/01
# Version 0.2.0
# pathutils.py
# Functions useful for working with files and paths.
# http://www.voidspace.org.uk/python/recipebook.shtml#utils

# Copyright Michael Foord 2004
# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/documents/BSD-LICENSE.txt

# For information about bugfixes, updates and support, please join the Pythonutils mailing list.
# http://voidspace.org.uk/mailman/listinfo/pythonutils_voidspace.org.uk
# Comments, suggestions and bug reports welcome.
# Scripts maintained at http://www.voidspace.org.uk/python/index.shtml
# E-mail fuzzyman@voidspace.org.uk

"""
This module contains convenience functions for working with files and paths.

Most of the functions are quite straightforward - all have useful docstrings.
"""

from __future__ import generators
import os
import sys

######################################
# Functions to read and write files in text and binary mode.

def readlines(filename):
    """Passed a filename, it opens that file, reads it, closes it
    and returns it as a list of lines."""
    filehandle = open(filename, 'r')
    outfile = filehandle.readlines()
    filehandle.close()
    return outfile

def writelines(filename, infile, newline = 0):
    """Passed a filename and a list of lines, it opens that file, writes the lines and closes it.
    If newline is set to 1 then it adds a '\n' to the end of each line."""
    filehandle = open(filename, 'w')
    for line in infile:
        if newline:
            line = line + '\n'
        filehandle.write(line)
    filehandle.close()


def readbinary(filename):
    """Read a file in binary format."""
    filehandle = open(filename, 'rb')
    thisfile = filehandle.read()
    filehandle.close()
    return thisfile

def writebinary(filename, thisfile):
    """Write a file in binary format."""
    filehandle = open(filename, 'wb')
    filehandle.write(thisfile)
    filehandle.close()


def readfile(filename):
    """Passed a filename it opens it, reads it, and closes it."""
    filehandle = open(filename, 'r')
    outfile = filehandle.read()
    filehandle.close()
    return outfile

def writefile(filename, infile):
    """Passed a filename and some text it opens that file, writes it and closes it."""
    filehandle = open(filename, 'w')
    filehandle.write(infile)
    filehandle.close()
    
####################################################################
# Some functions for dealing with paths

def tslash(apath):
    """Add a trailing slash to a path if it needs one.
    Doesn't use os.sep because you end up jiggered on windoze - when you want separators for URLs.
    """
    if apath and apath != '.' and not apath.endswith('/') and not apath.endswith('\\'):
        return apath + '/'
    else:
        return apath

def relpath(origin, dest):
    """Return the relative path between origin and dest.
    If it's not possible return dest.
    If they are identical return os.curdir
    Adapted from path.py by Jason Orendorff.
    """
    origin = os.path.abspath(origin).replace('\\', '/')
    dest = os.path.abspath(dest).replace('\\', '/')

    orig_list = splitall(os.path.normcase(origin))
    # Don't normcase dest!  We want to preserve the case.
    dest_list = splitall(dest)

    if orig_list[0] != os.path.normcase(dest_list[0]):
        # Can't get here from there.
        return dest

    # Find the location where the two paths start to differ.
    i = 0
    for start_seg, dest_seg in zip(orig_list, dest_list):
        if start_seg != os.path.normcase(dest_seg):
            break
        i += 1

    # Now i is the point where the two paths diverge.
    # Need a certain number of "os.pardir"s to work up
    # from the origin to the point of divergence.
    segments = [os.pardir] * (len(orig_list) - i)
    # Need to add the diverging part of dest_list.
    segments += dest_list[i:]
    if len(segments) == 0:
        # If they happen to be identical, use os.curdir.
        return os.curdir
    else:
        return os.path.join(*segments).replace('\\', '/')

def splitall(loc):
    """ Return a list of the path components in this path.

    The first item in the list will be  either os.curdir, os.pardir, empty,
    or the root directory of loc (for example, '/' or 'C:\\').
    The other items in the list will be strings.
    
    Adapted from path.py by Jason Orendorff.
    """
    parts = []
    while loc != os.curdir and loc != os.pardir:
        prev = loc
        loc, child = os.path.split(prev)
        if loc == prev:
            break
        parts.append(child)
    parts.append(loc)
    parts.reverse()
    return parts

#######################################################################
# a pre 2.3 walkfiles function - adapted from the path module by Jason Orendorff

join = os.path.join
isdir = os.path.isdir
isfile = os.path.isfile

def walkfiles(thisdir):
    """ walkfiles(D) -> iterator over files in D, recursively.
    """
    for child in os.listdir(thisdir):
        thischild = join(thisdir, child)
        if isfile(thischild):
            yield thischild
        elif isdir(thischild):
            for f in walkfiles(thischild):
                yield f
                
def walkdirs(thisdir):
    """
    Walk through all the subdirectories in a tree.
    """
    for child in os.listdir(thisdir):
        thischild = join(thisdir, child)
        if isfile(thischild):
            continue
        elif isdir(thischild):
            for f in walkdirs(thischild):
                yield f
            yield thischild
            
def walkemptydirs(thisdir):
    """This function is used to find empty directories - which will be missed by the walkfiles function."""
    if not os.listdir(thisdir):       # if the directory is empty.. then yield it
        yield thisdir   
    for child in os.listdir(thisdir):
        thischild = join(thisdir, child)
        if isdir(thischild):
            for emptydir in walkemptydirs(thischild):
                yield emptydir

###############################################################
# formatbytes takes a filesize (as returned by os.getsize() )
# and formats it for display in one of two ways !!

def formatbytes(sizeint, configdict=None, **configs):
    """Given a sizeint in bytes it formats a string
    to display the size of a file.
    The way this is done is either controlled by keywords passed in or a configdict passed in.
    Missing keywords will have default values substituted. Keywords and defaults are as follows :
    forcekb = 0,         If set this forces the output to be in terms of kilobytes and bytes only.
    largestonly = 1,    If set, instead of outputting '1 Mbytes, 307 Kbytes, 478 bytes' it outputs using only the
                        largest denominator - e.g. '1.3 Mbytes' or '17.2 Kbytes'
    kiloname = 'Kbytes',    The string to use for kilobytes
    meganame = 'Mbytes', The string to use for Megabytes
    bytename = 'bytes',     The string to use for bytes

    nospace = 1,        If set it outputs '1Mbytes, 307Kbytes' - notice there is no space

    Example outputs :
    19Mbytes, 75Kbytes, 255bytes
    2Kbytes, 0bytes
    23.8Mbytes

    NOTE :
    It uses the plural form even for singular
    It only displays the first digit after the decimal point - 1.19 = 1.1 !
    It still displays the decimal.
    """
    defaultconfigs = { 'forcekb' : 0, 'largestonly' : 1, 'kiloname' : 'Kbytes',
                       'meganame' : 'Mbytes', 'bytename' : 'bytes', 'nospace' : 1}
    if configdict is None:
        configdict = {}
    for entry in configs:
        configdict[entry] = configs[entry]  # keyword parameters override the dictionary passed in

    for keyword in defaultconfigs:
        if not configdict.has_key(keyword):
            configdict[keyword] = defaultconfigs[keyword]

    if configdict['nospace']:
        space = ''
    else:
        space = ' '
            
    mb, kb, rb = bytedivider(sizeint)
    if configdict['largestonly']:
        if mb and not configdict['forcekb']:
            return stringround(mb, kb)+ space + configdict['meganame']
        elif kb or configdict['forcekb']:
            if mb and configdict['forcekb']:
                kb += 1024*mb
            return stringround(kb, rb) + space+ configdict['kiloname']
        else:
            return str(rb) + space + configdict['bytename']
    else:
        outstr = ''
        if mb and not configdict['forcekb']:
            outstr = str(mb) + space + configdict['meganame'] +', '
        if kb or configdict['forcekb'] or mb:
            if configdict['forcekb']:
                kb += 1024*mb
            outstr += str(kb) + space + configdict['kiloname'] +', '
        return outstr + str(rb) + space + configdict['bytename']

def stringround(main, rest):
    """Given a file size in either (mb, kb) or (kb, bytes) - round it appropriately."""
    value = main + rest/1024.0  # divide an int by a float... get a float
    return str(round(value, 1))

def bytedivider(nbytes):
    """Given an integer (probably a long integer returned by os.getsize() ) it returns a tuple
    of (megabytes, kilobytes, bytes).
    This can be more easily converted into a formatted string to display the size of the file."""
    mb, remainder = divmod(nbytes, 1048576)
    kb, rb = divmod(remainder, 1024)
    return (mb, kb, rb)

########################################

def fullcopy(src, dst):
    """Copy file from src to dst.
    If the dst directory doesn't exist, we will attempt
    to create it using makedirs."""
    import shutil
    if not os.path.isdir(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))
    shutil.copy(src, dst)    

"""

Changelog
==========
2005/06/01      Version 0.2.0
Added walkdirs generator.


2005/03/11      Version 0.1.1
Added rounding to formatbytes and improved bytedivider with divmod.
Now explicit keyword parameters override the configdict in formatbytes.

2005/02/18      Version 0.1.0
The first numbered version.
"""
