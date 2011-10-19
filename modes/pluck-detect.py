#!/usr/bin/env python

import sys
import math

import numpy
import scipy.stats
import pylab
import matplotlib

import marsyas_interface
import harmonics_data

num_modes = 60

REQUIRE_TRIALS_PERCENT = 0.75
FIT_FROM_NODE_BEGIN = 0
FIT_FROM_NODE_END = 8
#FIT_FROM_NODE_PERCENT = 0.0
USE_FIT_FROM_NODE = 0

HEADER_BEGIN = """/* This file was automatically generated */
{
"""
HEADER_BOTTOM = """}
"""


try:
    basename = sys.argv[1]
except:
    print "need the instrument-string (i.e. violin-g )"
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
    n_more = range(30) # we want to predict this many
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
    if len(values) < 4:
        return scipy.stats.gmean(values)
    values = list(values)
    values.sort()
    discard = int(len(values)/4)
    main = values[discard:-discard]
    return scipy.stats.gmean(main)

def make_nodes(tns):
    nodes = []
    for tns in tnss:
        for i, tn in enumerate(tns):
            if len(nodes) <= i:
                nodes.append([])
            nodes[i].append(tn)
    # first mode is most trustworthy
    num_modes_found = len(nodes[0])
    for i, n in enumerate(nodes):
        if len(n) >= num_modes_found * REQUIRE_TRIALS_PERCENT:
            nodes[i] = iqgm(n)
        else:
            nodes[i] = None
    nodes = filter(lambda x: x is not None, nodes)
    return nodes


import scipy
import scipy.optimize

def make_extra_fits(nodes):
    ### extra fitting
    n = range(1, len(nodes)+1)

    #fit_node = FIT_FROM_NODE
    fit_node_end = FIT_FROM_NODE_END
    if fit_node_end > len(nodes):
        fit_node_end = len(nodes)
    #fit_node = int(FIT_FROM_NODE_PERCENT * len(nodes))
    consider = nodes[FIT_FROM_NODE_BEGIN:fit_node_end]
    n = n[FIT_FROM_NODE_BEGIN:fit_node_end]

    y = scipy.array(consider)
    x = scipy.array(n)
    def residuals(p, y, x):
        err = y - peval(x, p)
        return err

    # from Demoucron, p. 98
    def peval(x, p):
        return 1.0 / (p[0] + p[1]*((x-1)**2))

    guess = [3.0, 7.0]
    plsq = scipy.optimize.leastsq(residuals, guess,
        args=(y,x)
        )
    print plsq

    n_more = range(1, num_modes+1) # we want to predict this many
    yfit = []
    for n in n_more:
        value = peval(n, plsq[0])
        yfit.append(value)
    return yfit


harmonics = harmonics_data.HarmonicsData(basename)
tnss = harmonics.tnss
tsss = harmonics.tsss

nodes = make_nodes(tnss)
extra_fits = make_extra_fits(nodes)

plot_all_modes(nodes, extra_fits)

#plot_all_modes_log(nodes, extra_fits)


predicted_modes = []
for n in nodes:
    predicted_modes.append(n)
for i in range(len(nodes), len(extra_fits)):
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
    use_fit = min(USE_FIT_FROM_NODE, len(nodes))
    for i in range(use_fit):
        n = nodes[i]
        outfile.write("    %.8g,\n" % (1.0/n) )
    for i in range(use_fit, len(extra_fits)):
        e = extra_fits[i]
        outfile.write("    %.8g,\n" % (1.0/e) )
    outfile.write(HEADER_BOTTOM)
    outfile.close()

write_h(basename, nodes, extra_fits)

