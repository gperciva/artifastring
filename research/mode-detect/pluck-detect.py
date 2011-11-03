#!/usr/bin/env python

import sys
import math

import os.path

import partials
import operator
import numpy
import scipy.stats
import pylab
import matplotlib

#import marsyas_interface
import harmonics_data

PLOT_LATEST = 1

#num_modes = 85
num_modes = 30
#num_modes = 18

HEADER_BEGIN = """/* This file was automatically generated */
{
"""
HEADER_BOTTOM = """}
"""


try:
    dirname = sys.argv[1]
    basename = sys.argv[2]
except:
    print "need dir instrument-string (i.e. glasgow violin-g )"
    sys.exit(1)

def plot_normal(tns, png_filename):
    pylab.figure()
    n = range(1,len(tns)+1)
    pylab.plot(n, tns, 'o')
    pylab.xlabel("Modes of vibration")
    pylab.ylabel("Decay time")
    pylab.title("Decay times for %s" %
        instrument_string)
    pylab.savefig(png_filename.replace(".png", "-modes.png"))
    #pylab.show()

def plot_log(tns, png_filename):
    pylab.figure()
    tns_first = tns[0]
    tns_normed = map(lambda x: x/tns_first, tns)
    tns_log = map(math.log, tns_normed)
    n = range(1,len(tns)+1)
    pylab.plot(n, tns_log, 'o')
    pylab.xlabel("Modes of vibration")
    pylab.ylabel("Decay time")
    pylab.title("(log) Decay times for %s" %
        instrument_string)
    pylab.savefig(png_filename.replace(".png", "-modes-log.png"))

def plot_poly_fit(tns):
    pylab.figure()
    n = range(1,len(tns)+1)
    polycoeffs = scipy.polyfit(n, tns, -1)
    n_more = range(num_modes) # we want to predict this many
    yfit = scipy.polyval(polycoeffs, n_more)
    pylab.plot(n, tns, 'o')
    pylab.plot(n_more, yfit, '-')
    pylab.show()


#for tns, tss, harmonics, wav_filename, instrument_string in zip(tnss,
#        tsss, harmonicss, filenamess, instrument_strings):
#    png_filename = wav_filename.replace(".wav", ".png")
##    plot_decays(tss, tns, harmonics, png_filename, instrument_string)
#
##    plot_normal(tns, png_filename)
##    plot_log(tns, png_filename)
#    #plot_poly_fit(tns)



def plot_all_modes(nodes=None, extra_fit=None):

    pylab.figure()
    for i in range(len(tnss)):
        tns = tnss[i]
        n = range(1,len(tns)+1)
        pylab.semilogy(n, tns, '.')
    if nodes:
        iqgm_last = 0
        for i, m in enumerate(nodes):
            pylab.plot(i+1, m, 'bo')
            iqgm_last += 1
        en = range(1, len(extra_fit)+1)
        pylab.plot(en, extra_fit, 'r-')
    #
    pylab.xlabel("Modes of vibration")
    pylab.ylabel("Decay time")
    pylab.title("Decay times for %s" %
            basename)
    pylab.savefig(basename + "-modes.png")


def plot_all_modes_log(nodes, extra_fit):
    pylab.figure()
    for i in range(len(tnss)):
        tns = tnss[i]
        n = range(1,len(tns)+1)
        if SET_Y_ALL_MODES > 0:
            tns.append(SET_Y_ALL_MODES)
            n.append(0)
        #tns_first = tns[0]
        #tns_normed = map(lambda x: x/tns_first, tns)
        #tns_log = map(math.log, tns_normed)
        tns_log = map(math.log, tns)
        pylab.plot(n, tns_log, '.')
    iqgm_last = 0
    for i, m in enumerate(nodes):
        m = math.log(m)
        pylab.plot(i+1, m, 'bo')
        iqgm_last += 1
    en = range(1, len(extra_fit)+1)
    #print extra_fit
    extra_fit_log = map(math.log, extra_fit)
    pylab.plot(en, extra_fit_log, 'r-')
    #
    pylab.xlabel("Modes of vibration")
    pylab.ylabel("Decay time")
    pylab.title("(log) Decay times for %s" %
            instrument_string)
    pylab.savefig(filename_pattern.replace("*.wav", "-modes-all-log.png"))

def iqgm(values):
    # TODO: this doesn't handle fractional quartiles properly
    # http://en.wikipedia.org/wiki/Interquartile_mean#Dataset_not_divisible_by_four
    values = [ a for a in values if a is not None ]
    if len(values) < 4:
        return 0
    values.sort()
    discard = int(len(values)/4)
    main = values[discard:-discard]
    gmean = scipy.stats.gmean(main)
    mean = numpy.mean(main)
    return mean

def make_nodes(tnss, lenss):
    nodes = []
    decays = numpy.array(tnss)
    lengths = numpy.array(lenss)
    minimum_lengths = []
    for partial in range(len(lengths[0])):
        nonzero = []
        for trial in range(len(lengths)):
            if lengths[trial][partial] > 0:
                nonzero.append( lengths[trial][partial] )
        median_length = scipy.median(nonzero)
        if median_length > 0:
            minimum_lengths.append( 0.5*median_length )
        else: # is a NaN
            minimum_lengths.append( 0 )
    for trial in range(len(tnss)):
        #print tnss
        for partial in range(len(lengths[trial])):
            if lengths[trial][partial] < minimum_lengths[partial]:
                lengths[trial][partial] = 0
                tnss[trial][partial] = None
    nodes = []
    for tns in tnss:
        for i, tn in enumerate(tns):
            if len(nodes) <= i:
                nodes.append([])
            nodes[i].append(tn)
    # first mode is most trustworthy
    #num_modes_found = len(nodes[0])
    #modes = list(tnss)
    modeslen = []
    for i, n in enumerate(nodes):
        #if len(n) >= num_modes_found * REQUIRE_TRIALS_PERCENT:
        if len(n) >= 4:
            nodes[i] = iqgm(n)
            modeslen.append( 2*minimum_lengths[i] )
        else:
            nodes[i] = None
            modeslen.append(None)
    #nodes = filter(lambda x: x is not None, nodes)
    return nodes, modeslen, tnss


import scipy
import scipy.optimize

solution_count = 0
def make_extra_fits(pair):
    nodes = pair[0]
    lens = pair[1]
    if len(nodes) < 3:
        return

    ### extra fitting
    nos = range(1, len(lens)+1)

    consider = nodes
    nos_consider = nos

    x = []
    y = []
    weights = []
    for i, c in enumerate(consider):
        if c > 0:
            x.append( nos_consider[i] )
            y.append( 2*c )
            #weights.append( lens[i]**2 )
            #weights.append( lens[i] )
            weights.append( 1 )
            #weights.append( math.sqrt(lens[i]) )
        else:
            #print "skipping over node"
            pass
    x = scipy.array(x)
    y = scipy.array(y)
    weights = scipy.array(weights)
    #print '----'
    if len(x) == 0:
        return []

    hardcode_first = y[0]
    print x
    print y
    #print weights
    def residuals(p, y, x):
        #err = (y - peval(x, p)) * weights
        err = y - peval(x, p)
        return err

    B = 5.86e-5
    f0 = 659.7
    L = 0.33
    T = 80.0
    # from Demoucron, p. 98
    def peval(x, p):
        #if False:
        if True:
            if any(p < 0):
                return numpy.zeros(len(x))
            fn = partials.mode_B2freq(f0, x, B)
            wn = 2*numpy.pi*fn
            nf = p[0]
            na = p[1]
            nb = p[2]
            ns = ((T * (nf + na/wn) + B*nb*(x*numpy.pi/L)**2)
                / (T + B*(x*numpy.pi/L)**2))
            return ns
        #return 1.0 / (p[0] + p[1]*(x-1)**p[2])
        #return (p[0] + p[1]*(x-1)**2)
        #return (p[0] + p[1]*(x-1)**2)
        #return (hardcode_first + p[2]*((x-1)**1))
        return (hardcode_first + p[1]*((x-1)**2))
        #return (hardcode_first + p[1]*((x-1)))
        #return (hardcode_first + p[2]*(x-1) + p[1]*(x-1)**2)
        #return (hardcode_first + p[2]*(x-1) + p[1]*(x-1)**2)
        #return 1.0 / (p[0] + p[1]*numpy.exp(p[2]*(x-1)) )
        #return 1.0 / (p[0] + p[1]*(x-1)**2 )
        #return 1.0 / (p[0] + p[1]*(x)**2)
        #return numpy.exp(p[1]*(x-1))
        #return numpy.exp(p[0] + p[1]*(x-1))
        #return p[0] + p[1] / (p[2] + p[3]*x**2)
        #return p[0] + p[1] * numpy.exp(p[2]*x)
        #return p[0] + 1.0 / (p[1] + p[2]*(x-1)**2)

    #pylab.figure()
    guess = [1.0, 1.0, 1.0]
    #guess = [hardcode_first, 1.0, 1.0]
    #guess = [0.0, 1.0, 3.0, 0.1, 1.0, 1.0]
    #guess = [3.0, 3.0]
    plsq = scipy.optimize.leastsq(residuals, guess,
        args=(y,x)
        )
    p = plsq[0]
    print "solution:", p
    #res = residuals(p, y, x)
    #err = sum( res*res )
    predicted = peval(x, p)

    if PLOT_LATEST:
        global solution_count
        color = matplotlib.cm.jet(float(solution_count)/num_solutions)
        pylab.plot(x, y, 'o', color=color, label="%s" % (
            solution_count))
        solution_count += 1
        #pylab.semilogy(x,predicted, '-', color=color)
        #pylab.ylim([1e-2, 0.3])
        #print err

    n_more = range(1, num_modes+1) # we want to predict this many
    yfit = []
    for n in n_more:
        value = peval(n, plsq[0])
        yfit.append(value)
    if PLOT_LATEST:
        pylab.plot(n_more,yfit, '-', color=color)
        #pylab.semilogy(n_more,yfit, '-', color=color)

    #print plsq, yfit[-1]
    #pylab.semilogy(n_more,yfit, '-', color=color)
    return yfit


harmonics = harmonics_data.HarmonicsData(dirname, basename)
tnss = harmonics.tnss
tsss = harmonics.tsss
lenss = harmonics.lenss
filenames = harmonics.filenames

#    pylab.semilogy(h, 'o')
#pylab.show()

nodes, nodeslen, consider = make_nodes(tnss, lenss)
#for h in lenss:
#    print h
#for h in tnss:
#    print h

num_solutions = 0
for i, tns in enumerate(tnss):
    if len(tns) > 0:
        num_solutions = i+1
pylab.figure()
#nodes = make_nodes(tnss)
#extra_fits = map( make_extra_fits, zip(tnss, lenss) )
extra_fits = make_extra_fits( (nodes, nodeslen) )

#for i, e in enumerate(extra_fits):
#    print i, e

# pick median
#extra_fits = sorted(extra_fits, key=operator.itemgetter(-1))
#extra_fits = extra_fits[len(extra_fits)/2]
# TODO: total ick HACK
#highest_decay = 0.0
#keep_index = 0
#for i, e in enumerate(extra_fits):
#    #print highest_decay, e
#    if highest_decay < e[-1]:
#        highest_decay = e[-1]
#        keep_index = i
#print "keeping", keep_index
#extra_fits = extra_fits[keep_index]

if PLOT_LATEST:
    pylab.title(basename)

    print "plotting", len(consider), "trials"
    colors = {}
    for i, con in enumerate(consider):
        color = harmonics_data.bon_odori_color(filenames[i])
        splitlabel = os.path.basename(filenames[i]).split('-')[2:4]
        name = '-'.join(splitlabel)
        try:
            assert colors[color]
            label = None
        except:
            colors[color] = 1
            label = name
        #print label
        pylab.plot(
        #pylab.semilogy(
            [x+1
                for x,y in enumerate(con)
                if y is not None
               ],
            [ 2*x
                for x in con
                if x is not None
               ],
                '.',
                color=color, alpha=0.5,
                label=label)
    pylab.legend()
    pylab.xlim([0, num_modes])
    pylab.ylim([0, 100])
    #pylab.ylim([1e-4, 0.6])
    pylab.savefig(basename + "-modes.png")
    #pylab.show()
#exit(1)

#plot_all_modes(nodes, extra_fits)

#plot_all_modes_log(nodes, extra_fits)


predicted_modes = []
#for n in nodes:
#    predicted_modes.append(n)
for i in range(0, len(extra_fits)):
    e = extra_fits[i]
    predicted_modes.append(e)

#demoucron = []
#for i in range(len(predicted_modes)):
#    value = 1.0 / ( 3.0 + 7.0*(i-1)**2 )
#    demoucron.append( value )

#pylab.figure()
#pylab.semilogy(predicted_modes, label="predicted")
#pylab.semilogy(demoucron, label="demoucron")
#pylab.legend()
#pylab.savefig(basename + '-demoucron.png')
#pylab.show()

def write_h(basename, nodes, extra_fits):
    string_name = basename.replace('-', '_')
    string_name_caps = string_name.upper()
    num_modes = len(extra_fits)

    outfile = open(string_name + "_modes.h", 'w')
    outfile.write(HEADER_BEGIN % locals() )
    #use_fit = min(USE_FIT_FROM_NODE, len(nodes))
    #for i in range(use_fit):
    #    n = nodes[i]
    #    outfile.write("    %.8g,\n" % (1.0/n) )
    for i in range(len(extra_fits)):
        e = extra_fits[i]
        #outfile.write("    %.8g,\n" % (1.0/e) )
        outfile.write("    %.8g,\n" % (e) )
    outfile.write(HEADER_BOTTOM)
    outfile.close()

#write_h(basename, nodes, extra_fits)
write_h(basename, [], extra_fits)

