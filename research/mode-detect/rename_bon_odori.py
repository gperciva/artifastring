#!/usr/bin/env python
import sys
import glob
import os.path
import shutil
import numpy

try:
    order_filename = sys.argv[1]
    dirname = sys.argv[2]
except:
    print "Need order_filename and dirname"
    exit(1)

COLUMN_NAMES = ["half", "third", "golden", "low2", "fingerboard"]
ROW_NAMES = ["hard", "soft", "tissue", "hair"]
TAKE_NAMES = ["one", "two", "three"]

order = numpy.loadtxt(order_filename)

filenames = glob.glob(dirname + "*.wav")
filenames.sort()

for filename in filenames:
    basename = os.path.splitext(os.path.basename(filename))[0]
    splitname = basename.split('-')
    take = splitname[-2]
    number = int(splitname[-1])
    loc = numpy.where(order == number)
    col = loc[1][0]
    row = loc[0][0]
    #print number, col, row
    pluck_point = COLUMN_NAMES[col]
    plectrum = ROW_NAMES[row]

    take_index = TAKE_NAMES.index(take) + 1
    take_text = "%02i" % (take_index)
    #print take_text
    newname = splitname[0:2] + [pluck_point, plectrum, take_text]
    newname = '-'.join(newname) + '.wav'
    newname = os.path.join(dirname, newname)
    print newname
    shutil.move(filename, newname)


