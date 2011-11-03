#!/usr/bin/env python 

import sys

import numpy
import pylab
#import matplotlib
#YLIM = 2
YLIM = None

try:
    if sys.argv[2] != None:
        only_slips = True
except:
    only_slips = False

filename = sys.argv[1]

data = open(filename).readlines()
headers = data[0][1:].split('\t')
data = numpy.loadtxt(filename)

num_rows, num_columns = data.shape
seconds = data[:,0]
#print num_columns

pylab.figure()
for i in range(1,num_columns):
    if only_slips:
        if i != 5:
            continue
    column = data[:,i]
    #color = matplotlib.cm.jet((num_columns-float(i)) / (num_columns-1))
    pylab.plot(seconds, column,
        '.-',
        #color=color,
        label=headers[i])

if YLIM is not None:
    pylab.ylim([-YLIM,YLIM])
pylab.legend(loc=2)
pylab.title(filename)
pylab.show()



