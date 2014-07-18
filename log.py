#!/usr/bin/env python
# -*- coding: utf-8 -*-
# timegrep.py by Dennis Williamson 20100113
# in response to http://serverfault.com/questions/101744/fast-extraction-of-a-time-range-from-syslog-logfile

# thanks to serverfault user http://serverfault.com/users/1545/mike
# for the inspiration

# Perform a binary search through a log file to find a range of times
# and print the corresponding lines

# tested with Python 2.6

# TODO: Make sure that it works if the seek falls in the middle of
#       the first or last line
# TODO: Make sure it's not blind to a line where the sync read falls
#       exactly at the beginning of the line being searched for and
#       then gets skipped by the second read
# TODO: accept arbitrary date

# done: add -l long and -s short options
# done: test time format

version = "0.01a"

import os, sys
from stat import *
from datetime import date, datetime
import re
from optparse import OptionParser

# Function to read lines from file and extract the date and time
def getdata():
    """Read a line from a file

    Return a tuple containing:
        the date/time in a format such as 'Jan 15 20:14:01'
        the line itself

    The last colon and seconds are optional and
    not handled specially

    """
    try:
        line = handle.readline(bufsize)
    except:
        print("File I/O Error")
        exit(1)
    if line == '':
        print("EOF reached")
        exit(1)
    if line[-1] == '\n':
        line = line.rstrip('\n')
    else:
        if len(line) >= bufsize:
            print("Line length exceeds buffer size")
        else:
            print("Missing newline")
        exit(1)
    words = line.split(' ')
    if len(words) >= 3:
        linedate = words[0] + " " + words[1] + " " + words[2]
    else:
        linedate = ''
    return (linedate, line)

# End function getdata()

# Set up option handling
parser = OptionParser(version="%prog " + version)

parser.usage = "\n\t%prog [options] start-time end-time filename\n\n\
\twhere times are in the form hh:mm[:ss]"

parser.description = "Search a log file for a range of times occurring yesterday \
and/or today using the current time to intelligently select the start and end. \
A date may be specified instead. Seconds are optional in time arguments."

parser.add_option("-d", "--date", action="store", dest="date",
                  default="",
                  help="NOT YET IMPLEMENTED. Use the supplied date instead of today.")

parser.add_option("-l", "--long", action="store_true", dest="longout",
                  default=False,
                  help="Span the longest possible time range.")

parser.add_option("-s", "--short", action="store_true", dest="shortout",
                  default=False,
                  help="Span the shortest possible time range.")

parser.add_option("-D", "--debug", action="store", dest="debug",
                  default=0, type="int",
                  help="Output debugging information.\t\t\t\t\tNone (default) = %default, Some = 1, More = 2")

(options, args) = parser.parse_args()

if not 0 <= options.debug <= 2:
    parser.error("debug level out of range")
else:
    debug = options.debug    # 1 = print some debug output, 2 = print a little more, 0 = none

if options.longout and options.shortout:
    parser.error("options -l and -s are mutually exclusive")

if options.date:
    parser.error("date option not yet implemented")

if len(args) != 3:
    parser.error("invalid number of arguments")

start = args[0]
end = args[1]
file = args[2]

# test for times to be properly formatted, allow hh:mm or hh:mm:ss
p = re.compile(r'(^[2][0-3]|[0-1][0-9]):[0-5][0-9](:[0-5][0-9])?$')

if not p.match(start) or not p.match(end):
    print("Invalid time specification")
    exit(1)

# Determine Time Range
yesterday = date.fromordinal(date.today().toordinal() - 1).strftime("%b %d")
today = datetime.now().strftime("%b %d")
now = datetime.now().strftime("%R")

if start > now or start > end or options.longout or options.shortout:
    searchstart = yesterday
else:
    searchstart = today

if (end > start > now and not options.longout) or options.shortout:
    searchend = yesterday
else:
    searchend = today

searchstart = searchstart + " " + start
searchend = searchend + " " + end

try:
    handle = open(file, 'r')
except:
    print("File Open Error")
    exit(1)

# Set some initial values
bufsize = 4096  # handle long lines, but put a limit them
rewind = 100  # arbitrary, the optimal value is highly dependent on the structure of the file
limit = 75  # arbitrary, allow for a VERY large file, but stop it if it runs away
count = 0
size = os.stat(file)[ST_SIZE]
beginrange = 0
midrange = size / 2
oldmidrange = midrange
endrange = size
linedate = ''

pos1 = pos2 = 0

if debug > 0: print(
    "File: '{0}' Size: {1} Today: '{2}' Now: {3} Start: '{4}' End: '{5}'".format(file, size, today, now, searchstart,
                                                                                 searchend))

# Seek using binary search
while pos1 != endrange and oldmidrange != 0 and linedate != searchstart:
    handle.seek(midrange)
    linedate, line = getdata()    # sync to line ending
    pos1 = handle.tell()
    if midrange > 0:             # if not BOF, discard first read
        if debug > 1: print("...partial: (len: {0}) '{1}'".format((len(line)), line))
        linedate, line = getdata()

    pos2 = handle.tell()
    count += 1
    if debug > 0: print(
        "#{0} Beg: {1} Mid: {2} End: {3} P1: {4} P2: {5} Timestamp: '{6}'".format(count, beginrange, midrange, endrange,
                                                                                  pos1, pos2, linedate))
    if searchstart > linedate:
        beginrange = midrange
    else:
        endrange = midrange
    oldmidrange = midrange
    midrange = (beginrange + endrange) / 2
    if count > limit:
        print("ERROR: ITERATION LIMIT EXCEEDED")
        exit(1)

if debug > 0: print("...stopping: '{0}'".format(line))

# Rewind a bit to make sure we didn't miss any
seek = oldmidrange
while linedate >= searchstart and seek > 0:
    if seek < rewind:
        seek = 0
    else:
        seek = seek - rewind
    if debug > 0: print("...rewinding")
    handle.seek(seek)

    linedate, line = getdata()    # sync to line ending
    if debug > 1: print("...junk: '{0}'".format(line))

    linedate, line = getdata()
    if debug > 0: print("...comparing: '{0}'".format(linedate))

# Scan forward
while linedate < searchstart:
    if debug > 0: print("...skipping: '{0}'".format(linedate))
    linedate, line = getdata()

if debug > 0: print("...found: '{0}'".format(line))

if debug > 0: print(
    "Beg: {0} Mid: {1} End: {2} P1: {3} P2: {4} Timestamp: '{5}'".format(beginrange, midrange, endrange, pos1, pos2,
                                                                         linedate))

# Now that the preliminaries are out of the way, we just loop,
#     reading lines and printing them until they are
#     beyond the end of the range we want

while linedate <= searchend:
    print line
    linedate, line = getdata()

if debug > 0: print("Start: '{0}' End: '{1}'".format(searchstart, searchend))
handle.close()
