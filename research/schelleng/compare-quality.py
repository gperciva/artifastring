#!/usr/bin/env python

import numpy
import scipy
import scipy.stats
import glob
import pylab

import os
def get_immediate_subdirectories(dirname):
    return [int(name) for name in os.listdir(dirname)
        if os.path.isdir(os.path.join(dirname, name))]

def get_qs(dirnames, st, vel):
    #print "qualities for %.3f m/s" % vel
    qs = []
    dirnames = [ int(x.split('-')[1]) for x in dirnames]
    dirnames.sort()
    seen = []
    for dirname in dirnames:
        fs = dirname
        #filename = '%s/grid-%i-s%i-v%.3f.txt' % (dirname, fs, st, vel)
        filename = 'grids/grid-%i-s%i-v%.3f.txt' % (fs, st, vel)
        if filename not in seen:
            seen.append(filename)
        else:
            continue
        try:
            values = numpy.loadtxt(filename)
        except:
            continue

        f0_snr  = values[:,2]
        sfm_lim  = values[:,3]
        scn_lim = values[:,4]

        #ones = numpy.median(sfm_sub)
        #twos = numpy.max(sfm_sub)
        #threes = numpy.mean(sfm_sub)

        ones = numpy.median(sfm_lim)
        twos = numpy.mean(sfm_lim)
        threes = numpy.median(scn_lim)
        fours = numpy.mean(scn_lim)

        #ones = numpy.median(sfm_five)
        #twos = max(sfm_five)
        #threes = numpy.mean(sfm_five)

        #ones = numpy.median(f0_snr)
        #twos = numpy.max(f0_snr)
        #twos = scipy.stats.scoreatpercentile(f0_snr, 75)
        #threes = numpy.mean(f0_snr)

        #ones = scipy.stats.scoreatpercentile(sfm_five, 25)
        #twos = scipy.stats.scoreatpercentile(sfm_five, 75)

        #print dirname, ones, twos, threes
        qs.append( (fs/22050, ones, twos, threes, fours) )
    return numpy.array(qs)
    #    filename = '%s/grid-%i-s%i-v%.3f.txt' % (
    #        dirname, int(dirname), st, vel)
    #    quality = numpy.loadtxt(filename)
    #    print dirname, quality
      

#dirnames = get_immediate_subdirectories(os.getcwd())
#dirnames.sort()
dirnames = os.listdir('grids')

STRINGS = [0,1,2,3] 
COLORS = ['blue', 'green', 'purple', 'orange']
#STRINGS = [0] 
#STRINGS = [3] 
def draw_vel(st, vel, col):
    qs = get_qs(dirnames, st, vel)
    if len(qs) == 0:
        return

    #print qs[:,0]
    #print qs[:,1]
    pylab.plot(qs[:,0], qs[:,1], 'x-', label="sfm median %.1f" % vel, color=col)
    pylab.plot(qs[:,0], qs[:,2], '.-', label="sfm mean %.1f" % vel, color=col)
    pylab.plot(qs[:,0], qs[:,3], 'o-', label="scn median %.1f" % vel, color=col)
    pylab.plot(qs[:,0], qs[:,4], '.-.', label="scn mean %.1f" % vel, color=col)

    filename = "out/fs-st-%i-vel-%.3f.txt" % (st, vel)
    numpy.savetxt(filename, qs)

for i, st in enumerate(STRINGS):
    color = COLORS[i]
#    pylab.figure()
    draw_vel(st, 0.1, color)
    draw_vel(st, 0.4, color)
#    pylab.legend()
#    pylab.title("string %i" % st)

pylab.show()

#print values



