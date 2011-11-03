#!/usr/bin/env python

import os.path
import pickle

import numpy
import scipy.optimize
import pylab
import matplotlib

import defs
import partials

import tables

B3 = None

class ModePredict:
    def __init__(self, nf, nb, na, f0, B, T, L):
        self.nf = nf
        self.nb = nb
        self.na = na
        self.f0 = f0
        self.B = B
        self.T = T
        self.L = L

class ModePredict_stats:
    def __init__(self, basename, num_decays, highest_mode, rsquared):
        self.basename = basename
        self.num_decays = num_decays
        self.highest_mode = highest_mode
        self.rsquared = rsquared


def get_weight_var(n, xs, ys):
    cands = []
    for i, nn in enumerate(xs):
        if n == nn:
            cands.append(ys[i])
    if len(cands) < defs.Q_FIT_MIN_DISTINCT:
        return 0
    var = scipy.var(cands)
    return 1./var

def mode_func(p, x):
    if defs.MODES_FIXED_EXPONENT:
        return func_percival_fixed(p, x)
    else:
        return func_percival_variable(p, x)

def func_percival_variable(p, ns):
    #if p[0] < 0 or p[1] < 0 or p[2] < 1.0:
    if p[0] < mode_one_decay/2.0 or p[1] < 0 or p[2] < 1.0:
    #if p[0] < 0 or p[1] < 0:
        return 1e9*numpy.ones(len(ns))

    values = p[0] + p[1]*((ns-1.0)**p[2])
    return values

def func_percival_fixed(p, ns):
    if p[0] < 0 or p[1] < 0:
    #if p[0] < 0 or p[1] < 0:
        return 1e9*numpy.ones(len(ns))

    #values = p[0] + p[1]*((ns-1.0)**B3)
    #values = p[0] + p[1]*ns + p[2]*(ns**2)
    values = p[0] + p[1]*((ns-1.0)**2)
    #values = p[0] + p[1]*((ns-p[2])**2)
    return values

def residuals_weighted(p, y, x, weights):
    return (y - mode_func(p, x)) * weights

def fit_modes(xs, ys, weights):
    show = False
    xs = numpy.array(xs)
    ys = numpy.array(ys)
    weights = numpy.array(weights)
    ### because these will be squared
    weights = numpy.sqrt( weights )

    #decay_dict = split_into_list(xs, ys)
    #mode_one_decay = 2.0
    #if len(decay_dict[1]) > 1:
        #global mode_one_decay
        #mode_one_decay = numpy.mean( decay_dict[1] )
    #else:
    #    mode_one_decay = 2.0
    #try:
    #    mode_ten_decay = numpy.mean( decay_dict[11] )
    #    slope = (mode_ten_decay-mode_one_decay) / ((10-1)**B3)
    #    if slope != slope: # check for nan
    #        slope = 0.05
    #except:
    #    slope = 0.05

    ###### initial estimate
    #if defs.MODES_FIXED_EXPONENT:
    initial_guess = numpy.array([
            #mode_one_decay, slope, 0.1,
            1e-1, 1e-1,
            #1e-1, 1e-1, 1.0,
        ])
    #else:
    #    initial_guess = numpy.array([
    #        mode_one_decay, slope, B3,
    #    ])
    #print "initial:", initial_guess
    #exit(1)
    p,cov,infodict,mesg,ier = scipy.optimize.leastsq(
        residuals_weighted, initial_guess,
        args=(ys, xs, weights),
        full_output=1,
        )
    print "fit:", p

    #show=True
    eval_ns = numpy.array( list(set(xs)) )
    #print eval_ns
    if show:
        pylab.plot(xs, ys, '.')
        pylab.plot(eval_ns, mode_func(p, eval_ns), '-')
        pylab.show()


    if 1 < ier > 4:
        print "mode_decays.py: failed to minimize!"
    #if any(func_woodhouse_constraints(p) != 0):
    #    print "mode_decays.py: did not satisfy constraints!"

    return p

def split_into_list(xs, ys):
    decays = {}
    for i in range(max(xs)):
        decays[i+1] = []
    for i, n in enumerate(xs):
        decays[n].append(ys[i])
    for key, value in decays.items():
        if len(value) < defs.Q_FIT_MIN_DISTINCT:
            decays[key] = []
    return decays

def get_decays_means_stds(decay_list):
    stds = numpy.zeros(defs.TOTAL_HARMONICS)
    means = numpy.zeros(defs.TOTAL_HARMONICS)
    for i, d in enumerate(decay_list):
        d = decay_list[d]
        if len(d) >= defs.Q_FIT_MIN_DISTINCT:
            means[i] = scipy.mean(d)
            stds[i] = scipy.std(d)
        else:
            means[i] = 0
            stds[i] = 0
    return means, stds

def filter_Q(xs_orig, ys_orig, weights_orig):
    xs = []
    ys = []
    weights = []
    exclude_xs = []
    exclude_ys = []
    exclude_weights = []
    Q_list = split_into_list(xs_orig, ys_orig)
    Q_means, Q_stds = get_decays_means_stds(Q_list)

    if False:
        for key, value in Q_list.items():
            if len(value) > 2:
                xs.append(key)
                ys.append( scipy.median(value) )
                weights.append( 1./scipy.var(value) )
                #weights.append( 1. )
        xs = numpy.array(xs)
        ys = numpy.array(ys)
        weights = numpy.array(weights)
        #print xs
        #print ys
        #print weights
        exclude_xs = numpy.array(exclude_xs)
        exclude_ys = numpy.array(exclude_ys)
        exclude_weights = numpy.array(exclude_weights)
        return xs, ys, weights, exclude_xs, exclude_ys, exclude_weights
            

    def filt_min_num(y, m, s):
        if m == 0:
            return False
        return True
    def filt_std(y, m, s):
        if (m-3*s) < y < (m+3*s):
            return True
        return False
    def filt_std_total(y, m, s):
        if s < MAX_STD_Q_MODE:
            return True
        return False

    ab = split_into_list(xs_orig, ys_orig)
    cd = [a for a in ab if len(ab[a]) > defs.Q_FIT_MIN_DISTINCT ]
    highest_mode = max(cd)
    start_fit_at = int(highest_mode * defs.Q_FIT_START_AT_PERCENT)
    start_fit_at = min(highest_mode - defs.Q_FIT_END_AT_LEAST, start_fit_at)
    start_fit_at = max(highest_mode - defs.Q_FIT_END_AT_MOST, start_fit_at)
    start_fit_at = max(defs.Q_FIT_START_AT_MODE_MIN, start_fit_at)
    print "start fit at:", start_fit_at

    for i in xrange(len(xs_orig)):
        x = xs_orig[i]
        y = ys_orig[i]
        weight = weights_orig[i]
        #if filt(y, Q_means[x-1], Q_stds[x-1]):
        #if filt_std_total(y, Q_means[x-1], Q_stds[x-1]):
        #if filt_min_num(y, means[x-1], stds[x-1]):
        if x >= start_fit_at and x in cd:
            xs.append(x)
            ys.append(y)
            weights.append(weight)
        else:
            #print "exclude", x, y
            exclude_xs.append(x)
            exclude_ys.append(y)
            exclude_weights.append(weight)
    xs = numpy.array(xs)
    ys = numpy.array(ys)
    weights = numpy.array(weights)
    exclude_xs = numpy.array(exclude_xs)
    exclude_ys = numpy.array(exclude_ys)
    exclude_weights = numpy.array(exclude_weights)
    return xs, ys, weights, exclude_xs, exclude_ys, exclude_weights

def dot_color(rs):
    rss = 1./rs
    if rss > 1.0:
        rss = 1.0
    dot = '.'
    markersize = 5.0 + 5.0*(rss)
    color = matplotlib.cm.winter(1.-rss)
    return dot, color, markersize

def plot_losses(decays):
    pylab.figure()
    #print "# n, loss factor, weight"
    for d in decays:
        #print "%i, %.2e, %.2e" %(d.n, 1./d.Q, d.rsquared)
        dot, color, markersize = dot_color(d.variance)
        pylab.plot(d.n, 1./d.Q,
            dot, color=color,
            markersize=markersize,
            linewidth=0,
            )
        pylab.xlabel("mode")
        pylab.ylabel("loss factor")
        pylab.xlim([0, max([d.n for d in decays])+1])
        #pylab.legend()

HEADER_BEGIN = """/* This file was automatically generated */
{
"""
HEADER_BOTTOM = """}
"""
def write_h(basename, decays):
    string_name = basename.replace('-', '_')
    filename = os.path.join('out', string_name + "_modes.h")
    #string_name_caps = string_name.upper()

    outfile = open(filename, 'w')
    outfile.write(HEADER_BEGIN % locals() )
    for decay in decays:
        outfile.write("    %.8g,\n" % (decay) )
    outfile.write(HEADER_BOTTOM)
    outfile.close()

def write_pickle(basename, decays):
    pickle_filename = os.path.join('out',
        basename + ".mode-decays.pickle")
    pickle_file = open(pickle_filename, 'wb')
    pickle.dump( decays, pickle_file, -1)
    pickle_file.close()


def handle_decays(decayss, basename, f0, B, T, L, harmonic_stats,
        plot=False, recalc=False):
    #plot_losses(decayss)

    consider = '-'.join( basename.split('-')[0:3] )
    print consider
    global B3
    if "violin-e" in consider:
        B3 = 2.0
    else:
        B3 = 3.0
        #B3 = 2.0
    if not defs.MODES_FIXED_EXPONENT:
        if not "glasgow" in consider:
            B3 = 2.0
            #print "Error: can only safely evaluate the Glasgow recordings"
            #print "without a fixed exponent"
            #exit(1)

    nss = numpy.array([d.n for d in decayss])
    #Q = numpy.array([d.Q for d in decayss])
    alpha = numpy.array([d.alpha for d in decayss])

    weights = numpy.array([ 1. / d.variance for d in decayss])
    if defs.MODES_HACK_LIMIT_WEIGHTS_MIN and defs.MODES_HACK_LIMIT_WEIGHTS_MAX:
        weights = weights.clip(min=defs.MODES_HACK_LIMIT_WEIGHTS_MIN,
            max=defs.MODES_HACK_LIMIT_WEIGHTS_MAX)

    alpha_list = split_into_list(nss, alpha)
    weights_list = split_into_list(nss, weights)
    nss_use, alpha_use, weights_use, nss_exclude, alpha_exclude, weights_exclude = filter_Q(
        nss, alpha, weights)

    blank_triple_cutoff = 40
    missing = []
    for a in range(5,max(nss_use)):
        if a not in nss_use:
            missing.append(a)
    if len(missing) > 2:
        for a in range(5,max(nss_use)):
            if a in missing:
                if a+1 in missing:
                    if a+2 in missing:
                        blank_triple_cutoff = a
                        break
    #print nss_use
    #print blank_triple_cutoff
    nss_use_act = []
    alpha_use_act = []
    weights_use_act = []
    nss_exclude = list(nss_exclude)
    alpha_exclude = list(alpha_exclude)
    weights_exclude = list(weights_exclude)
    for n, a, w in zip(nss_use, alpha_use, weights_use):
        #print n, a
        if n < blank_triple_cutoff:
            nss_use_act.append(n)
            alpha_use_act.append(a)
            weights_use_act.append(w)
        else:
            nss_exclude.append(n)
            alpha_exclude.append(a)
            weights_exclude.append(w)
    nss_use = numpy.array(nss_use_act)
    alpha_use = numpy.array(alpha_use_act)
    weights_use = numpy.array(weights_use_act)

    #wns_use = 2*numpy.pi*partials.mode_B2freq(f0, nss_use, B)

    p = fit_modes(nss_use, alpha_use, weights_use)
    nss_eval = numpy.arange(1, defs.MODES_FIT_TO+1)
    pred = mode_func(p, nss_eval)
    #wns_eval = 2*numpy.pi*partials.mode_B2freq(f0, nss_eval, B)


    min_dots = harmonic_stats.num_files/2
    extra_n = []
    extra = []
    for n in range(1, int(max(pred))):
        try:
            consider = alpha_list[n]
            con_weight = weights_list[n]
        except:
            continue
        #std = scipy.std(consider)
        #mean = scipy.mean(consider)
        #median = scipy.median(consider)
        #print "%i\t%i\t%.3f\t%.3f\t%.3f\t%.3f" % (
        #    n, len(consider), std, mean, median, weighted_average)
        if len(consider) >= min_dots:
            weighted_average = scipy.average(consider, weights=con_weight)
            extra_n.append(n)
            extra.append(weighted_average)

    if defs.DECAYS_PLOT_USED:
        pylab.figure()
        pylab.plot(nss_use, alpha_use, '.')
        pylab.plot(nss_exclude, alpha_exclude, 'x', color="red")
        pylab.plot(nss_eval, pred, color="green")
        pylab.xlabel("mode")
        pylab.ylabel("Q")
        pylab.title(basename)
        pylab.show()

    if defs.DECAYS_PLOT_Q:
        pylab.figure()
        for d in decayss:
            #print "%i, %.2e, %.2e" %(d.n, 1./d.Q, d.rsquared)
            wei = 1./d.variance
            if wei > 1:
                wei = 1.
            dot, color, markersize = dot_color(wei)
            #pylab.plot(d.n, 1./d.Q,
            pylab.plot(d.n, d.Q,
                dot, color=color,
                markersize=markersize,
                linewidth=0,
                )
        pylab.plot(nss_eval, pred, color="red")
        pylab.xlabel("mode")
        pylab.ylabel("Q")
        pylab.show()
      
    #if False:
    if defs.DECAYS_PLOT_DECAYS:
        pylab.figure()
        for d in decayss:
            #print "%i, %.2e, %.2e" %(d.n, 1./d.Q, d.rsquared)
            #print d.variance
            dot, color, markersize = dot_color(d.variance)
            pylab.plot(d.n, d.alpha,
            #pylab.plot(d.w, d.alpha,
                dot, color=color,
                markersize=markersize,
                linewidth=0,
                )
            pylab.xlabel("mode")
            pylab.ylabel("alpha")
        for i in range(len(extra)):
            pylab.plot(extra_n[i], extra[i],
                'o',
                color="orange")
        #pylab.plot(nss_eval, wns_eval / (2*pred), color="red")
        pylab.plot(nss_eval, pred, color="red")
        pylab.show()

    predicted = mode_func(p, nss_use)
    #print "fit:", p

    ys = alpha_use
    #ys = Q_use
    alpha_use = ys
    ss_err = ((ys - predicted)**2).sum()
    ss_tot = ((ys-ys.mean())**2).sum()
    rsquared = 1. - (ss_err / ss_tot)

    pred_combo = []
    for i in range(1, defs.MODES_FIT_TO+1):
        try:
            ind = extra_n.index(i)
            alpha = extra[ind]
        except:
            alpha = pred[i-1]
        pred_combo.append(alpha)
    pred_combo = numpy.array(pred_combo)


    stats = ModePredict_stats(basename, len(nss_use), max(nss_use), rsquared)
    stats.alpha_1 = pred_combo[0]
    stats.alpha_2 = pred_combo[1]
    stats.alpha_3 = pred_combo[2]
    stats.alpha_4 = pred_combo[3]
    stats.alpha_5 = pred_combo[4]
    stats.alpha_10 = pred_combo[9]
    #stats.alpha_40 = pred_combo[39]


    basename = tables.anonymize_name(basename)
    filename = os.path.join('out', basename+".predicted.modes.txt")
    #ns_deted = numpy.arange(1, highest_safe)
    ns_deted = numpy.arange(1, defs.MODES_FIT_TO + 1)
    pred_deted = mode_func(p, ns_deted)
    data = numpy.vstack((ns_deted, pred_deted)).transpose()
    numpy.savetxt(filename, data)

    filename = os.path.join('out', basename+".detected.modes.txt")
    data = numpy.vstack((nss_use, alpha_use)).transpose()
    numpy.savetxt(filename, data)

    filename = os.path.join('out', basename+".model.modes.txt")
    data = numpy.vstack(pred_combo)
    numpy.savetxt(filename, data)

    filename = os.path.join('out', basename+".detected.omit.txt")
    data = numpy.vstack((nss_exclude, alpha_exclude)).transpose()
    numpy.savetxt(filename, data)

    #write_h(basename, pred_combo)
    #write_pickle(basename, pred_combo)
    #write_h(basename, pred)
    write_pickle(basename, pred_combo)

    #print
    #print
    #print stats.rsquared
    #print
    #print
    return p[0], p[1], stats

