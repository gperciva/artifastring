#!/usr/bin/env python

DISABLE_MULTI = False
DISABLE_MULTI = True
DEBUG = 0
#DEBUG = 4

PLOT_PNG_BARE = False
PLOT_PNG_BARE = True

PLOT_STD = False
#PLOT_STD = True
PLOT_COMBO = False
#PLOT_COMBO = True
LOGS = True
#LOGS = False

import pickle
import os
import numpy
import pylab
pylab.ioff()

import multi_artifastring
import actual
import defs

XB_MIN = 0.10
XB_MAX = 0.20

if DEBUG == 0:
    STEPS_FORCE = 200
    STEPS_POSITIONS = 200
    NUM_NOTES = 25
elif DEBUG == 1:
    STEPS_FORCE = 3
    STEPS_POSITIONS = 3
    NUM_NOTES = 1
elif DEBUG == 2:
    STEPS_FORCE = 10
    STEPS_POSITIONS = 20
    NUM_NOTES = 1
elif DEBUG == 3:
    STEPS_FORCE = 10
    STEPS_POSITIONS = 20
    NUM_NOTES = 5
elif DEBUG == 4:
    STEPS_FORCE = 20
    STEPS_POSITIONS = 50
    NUM_NOTES = 5
STEPS_X = STEPS_POSITIONS
STEPS_Y = STEPS_FORCE


def generic_init(actions):
    st = actions['st']
    fp = actions['fp']
    xb = actions['xb']
    fb = actions['fb']
    vb = actions['vb']
    ba = actions['ba']
    return st, fp, xb, fb, vb, ba

class AxisLabel():
    def __init__(self, title, low, high, num, log):
        self.title = title
        self.low = low
        self.high = high
        self.num = num
        self.log = log


def generate_schelleng_force(dirname, name):
    actions = defs.INVESTIGATE[name]['actions']
    force_args = defs.INVESTIGATE[name]['var_forces']
    st, fp, xb, fb, vb, ba = generic_init(actions)

    if LOGS:
        forces = numpy.exp(numpy.linspace(
            numpy.log(force_args[0]),
            numpy.log(force_args[1]),
            STEPS_FORCE))
        positions = numpy.exp(numpy.linspace(
            numpy.log(XB_MIN),
            numpy.log(XB_MAX),
            STEPS_POSITIONS))
    else:
        forces = numpy.linspace(force_args[0], force_args[1], STEPS_FORCE)
        positions = numpy.linspace(XB_MIN, XB_MAX, STEPS_POSITIONS)
    #print forces
    #print positions
    #exit(1)
    xlabel = AxisLabel("x_b", XB_MIN, XB_MAX, len(positions), LOGS)
    ylabel = AxisLabel("F_b", force_args[0], force_args[1], len(forces), LOGS)

    argss = []
    for i, fb in enumerate(forces):
        for j, xb in enumerate(positions):
            basename = "%s-s%i-p%.3f-f%.3f-v%.3f-a%.3f" % (
                "%s/bow" % dirname, st, xb, fb, vb, ba)
            #print bp, force, vel
            act = dict(actions)
            act['fb'] = fb
            act['fb2'] = None
            act['xb'] = xb
            act['ba'] = ba
            act['i'] = i
            act['j'] = j
            args = (act, basename, NUM_NOTES)
            argss.append(args)
    return argss, xlabel, ylabel

def generate_schelleng_finger_position(dirname, name):
    actions = defs.INVESTIGATE[name]['actions']
    force_args = defs.INVESTIGATE[name]['var_forces']
    st, fp, xb, fb, vb, ba = generic_init(actions)

    forces = numpy.linspace(force_args[0], force_args[1], STEPS_FORCE)
    finger_positions = numpy.linspace(0.0, 0.333, STEPS_POSITIONS)
    xlabel = AxisLabel("x_f", 0.0, 0.333, len(finger_positions),
        LOGS)
    ylabel = AxisLabel("F_b", force_args[0], force_args[1], len(forces),
        LOGS)

    argss = []
    for i, fb in enumerate(forces):
        for j, fp in enumerate(finger_positions):
            basename = "%s-s%i-p%.3f-f%.3f-v%.3f-fp%.3f" % (
                "%s/bow" % dirname, st, xb, fb, vb, fp)
            #print bp, force, vel
            act = dict(actions)
            act['fb'] = fb
            act['fb2'] = None
            act['fp'] = fp
            #act['xb'] = xb
            #act['ba'] = ba
            act['i'] = i
            act['j'] = j
            args = (act, basename, NUM_NOTES)
            argss.append(args)
    return argss, xlabel, ylabel


def generate_schelleng_velocity(dirname, name):
    actions = defs.INVESTIGATE[name]['actions']
    force_args = defs.INVESTIGATE[name]['var_forces']
    st, fp, xb, fb, vb, ba = generic_init(actions)

    vel_low = 0.1
    vel_high = 0.5
    vels = numpy.linspace(vel_low, vel_high, STEPS_POSITIONS)
    #positions = numpy.linspace(XB_MIN, XB_MAX, STEPS_POSITIONS)
    #xlabel = AxisLabel("x_b", XB_MIN, XB_MAX, len(positions))
    forces = numpy.linspace(force_args[0], force_args[1], STEPS_FORCE)
    xlabel = AxisLabel("F_b", force_args[0], force_args[1],
        len(forces), LOGS)
    ylabel = AxisLabel("v_b", vel_low, vel_high, len(vels), LOGS)

    argss = []
    for i, vb in enumerate(vels):
        for j, fb in enumerate(forces):
            basename = "%s-s%i-p%.3f-f%.3f-v%.3f-a%.3f" % (
                "%s/bow" % dirname, st, xb, fb, vb, ba)
            #print bp, force, vel
            act = dict(actions)
            act['vb'] = vb
            act['fb'] = fb
            act['fb2'] = None
            act['xb'] = xb
            act['ba'] = ba
            act['i'] = i
            act['j'] = j
            args = (act, basename, NUM_NOTES)
            argss.append(args)
    return argss, xlabel, ylabel



def generate_accel(dirname, name):
    actions = defs.INVESTIGATE[name]['actions']
    force_args = defs.INVESTIGATE[name]['var_forces']
    st, fp, xb, fb, vb, ba = generic_init(actions)

    #ba_low = 1.0
    #ba_high = 10.0
    #accels = numpy.linspace(ba_low, ba_high, STEPS_X)
    fb2_low = 0.25
    fb2_high = 1.0
    fb2s = numpy.linspace(fb2_low, fb2_high, STEPS_POSITIONS)
    xlabel = AxisLabel("F_b2", fb2_low, fb2_high, len(fb2s), LOGS)
    forces = numpy.linspace(force_args[0], force_args[1], STEPS_FORCE)
    ylabel = AxisLabel("F_b", force_args[0], force_args[1],
        len(forces), LOGS)

    argss = []
    for i, fb in enumerate(forces):
        for j, fb2 in enumerate(fb2s):
            basename = "%s-s%i-p%.3f-f%.3f-v%.3f-a%.3f" % (
                "%s/bow" % dirname, st, xb, fb, vb, fb2)
            act = dict(actions)
            act['fb'] = fb
            act['xb'] = xb
            act['fb2'] = fb2
            act['ba'] = ba
            act['i'] = i
            act['j'] = j
            args = (act, basename, NUM_NOTES)
            argss.append(args)
    return argss, xlabel, ylabel


def generate(name, populate_func):
    inst_args = defs.INVESTIGATE[name]['inst']
    expected_f0 = defs.INVESTIGATE[name]['expected_f0']
    actions = defs.INVESTIGATE[name]['actions']
   

    
    dirname=os.path.join("/tmp/art", name)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    argss, xlabel, ylabel = populate_func(dirname, name)

    
    shared_init_args = (inst_args[0], inst_args[1], expected_f0)
    
    print "Map (performing %i simulations)..." % (len(argss)*NUM_NOTES)
    queue = multi_artifastring.task(actual.process, argss,
        actual.make_shared, shared_init_args,
        disable_multi=DISABLE_MULTI)
    
    print "Reduce (analyze %i simulations)..." % (len(argss)*NUM_NOTES)

    coll = []
    while not queue.empty():
        #(filenames, actions, means, stds, sfmm, sfmstd) = queue.get()
        (filenames, actions, means, stds) = queue.get()
        xb = actions['xb']
        force = actions['fb']
        i = actions['i']
        j = actions['j']
    
        value = (xb, force, i, j, means, stds)
        #value = (xb, force, i, j, sfmm, sfmstd)
        coll.append(value)
    coll.sort()

    data = (coll, xlabel, ylabel)

    pickle_filename = os.path.join(dirname, 'coll.pickle')
    pickle.dump(data, open(pickle_filename, 'wb'))
    print "... done"
    


def display(name):
    dirname=os.path.join("/tmp/art", name)
    pickle_filename = os.path.join(dirname, 'coll.pickle')
    display_filename(pickle_filename)


def display_filename(pickle_filename, name=None):
    print "Loading data to display..."
    data = pickle.load(open(pickle_filename, 'rb'))
    coll, xlabel, ylabel = data

    if not name:
        name = pickle_filename.split('/')[3]

    def normalize(val, low, high):
        return (val-low) / (high-low)

    num_features = actual.NUM_FEATURES
    ms = []
    ss = []
    for i in range(num_features):
        ms.append([])
        ss.append([])

    # find ranges of values
    for value in coll:
        (bp, force, i, j, means, stds) = value
        #(bp, force, i, j, sfmm, sfmstd) = value
        for i in range(num_features):
            ms[i].append(means[i])
            ss[i].append(stds[i])
        #ms[0].append(sfmm)
        #ss[0].append(sfmstd)

    print "Generating plots..."
    #m = 0
    ### for schelleng force
    ri = 7
    gi = 0
    bi = 7
    ### for accel?
    #ri = 0
    #gi = 1
    #bi = 7
    power = 0.5
    invert = False
    #invert = True

    if PLOT_PNG_BARE:
        fig = pylab.figure()
        fig.set_size_inches(4,3)
        ax = pylab.Axes(fig, [0., 0., 1., 1.,])
    else:
        fig = pylab.figure()
        pylab.title("%s" % (name))
    fig.set_size_inches(16,12)
    numx = xlabel.num
    numy = ylabel.num
    img = numpy.zeros( (numy, numx, 3), dtype=numpy.float32 )

    min_ms_ri = min(ms[ri])
    min_ms_gi = min(ms[gi])
    min_ms_bi = min(ms[bi])
    max_ms_ri = max(ms[ri])
    max_ms_gi = max(ms[gi])
    max_ms_bi = max(ms[bi])

    min_ss_ri = min(ms[ri])
    max_ss_ri = max(ms[ri])
    print "got min/max"
    for value in coll:
        (bp, force, i, j, means, stds) = value
        #(bp, force, i, j, sfmm, sfmstd) = value
        x = bp
        y = force
        #r = normalize(means[ri], min(ms[ri]), max(ms[ri]))
        g = normalize(means[gi], min_ms_gi, max_ms_gi)
        b = normalize(means[bi], min_ms_bi, max_ms_bi)

        r = normalize(stds[ri], min_ss_ri, max_ss_ri)
        if invert:
            r = 1. - r**power
            g = 1. - g**power
            b = 1. - b**power
        else:
            r = r**power
            g = g**power
            b = b**power
        #text = "%.3f\t%.3f\t%.3f\t%.3f\t%.3f" % (x,y,r,g,b)
        #out.write(text + "\n")

        #pylab.plot(x,y, '.', color=(r,g,b), markersize=10)
        #pylab.semilogy(x,y, '.', color=(r,g,b), markersize=10)
        img[i][j][0] = r
        img[i][j][1] = g
        img[i][j][2] = b
    print "start imshow"
    if PLOT_PNG_BARE:
        ax.imshow(img,
            #interpolation='bilinear',
            aspect="auto",
            origin="lower",
        )
        ax.set_xlim(0, numx-1)
        ax.set_ylim(0, numy-1)
    else:
        pylab.imshow(img,
            #interpolation='bilinear',
            aspect="auto",
            origin="lower",
        )
        pylab.xlim(0, numx-1)
        pylab.ylim(0, numy-1)
    print "end imshow"
    for m in range(5, 10):
        modal = 1.0 / m
        relpos = 1.0 - (xlabel.high - modal) / (xlabel.high - xlabel.low)
        abspos = relpos * (numx-1)
        print abspos,
        if xlabel.log:
            abspos = numpy.log(abspos)
        print abspos
        #print m, modal, relpos, abspos
        if PLOT_PNG_BARE:
            pass
            #ax.axvline(abspos, color="yellow")
        else:
            #pylab.axvline(abspos, color="yellow")
            pass

    xlocs = numpy.linspace(0, numx-1, 11)
    ylocs = numpy.linspace(0, numy-1, 11)
    if xlabel.log:
        xticks = map( lambda d: str("%.3f" % d),
            numpy.exp(numpy.linspace(
                numpy.log(xlabel.low),
                numpy.log(xlabel.high),
                len(xlocs))))
    else:
        xticks = map( lambda d: str("%.3f" % d),
            numpy.linspace(xlabel.low, xlabel.high, len(xlocs)))
    if ylabel.log:
        yticks = map( lambda d: str("%.2f" % d),
            numpy.exp(numpy.linspace(
                numpy.log(ylabel.low),
                numpy.log(ylabel.high),
                len(ylocs))))
    else:
        yticks = map( lambda d: str("%.2f" % d),
            numpy.linspace(ylabel.low, ylabel.high, len(ylocs)))
    if True:
        pylab.xticks(xlocs, xticks)
        pylab.xlabel(xlabel.title)
    
        pylab.yticks(ylocs, yticks)
        pylab.ylabel(ylabel.title)
     
    if PLOT_STD:
        pylab.figure()
        pylab.title("Standard deviations for %s" % (name))
        pylab.xlim(XB_MIN, XB_MAX)
        power = 0.5
        for value in coll:
            (bp, force, i, j, means, stds) = value
            x = bp
            y = force
            r = normalize(stds[ri], min(ss[ri]), max(ss[ri]))
            g = normalize(stds[gi], min(ss[gi]), max(ss[gi]))
            b = normalize(stds[bi], min(ss[bi]), max(ss[bi]))
            r = r**power
            g = g**power
            b = b**power
            pylab.plot(x,y, '.', color=(r,g,b), markersize=10)
    if PLOT_COMBO:
        pylab.figure()
        pylab.title("Combo for %s" % (name))
        pylab.xlim(XB_MIN, XB_MAX)
        power = 0.5
        ri = 0
        gi = 3
        bi = 3
        for value in coll:
            (bp, force, i, j, means, stds) = value
            x = bp
            y = force
            r = normalize(means[ri], min(ms[ri]), max(ms[ri]))
            g = normalize(stds[gi], min(ss[gi]), max(ss[gi]))
            b = normalize(means[bi], min(ms[bi]), max(ms[bi]))
            r = r**power
            g = g**power
            b = b**power
            pylab.plot(x,y, '.', color=(r,g,b), markersize=10)
    #pylab.axis('off')
    #pylab.yscale('log')
    filename= name + ".png"
    if PLOT_PNG_BARE:
        ax.set_axis_off()
        fig.add_axes(ax)
        #pylab.title('')
    #pylab.savefig(name+".png", bbox_inches='tight', pad_inches=0)
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        pylab.savefig(filename, bbox_inches=extent)
        print "filename:\tX:", xlabel.title, xlabel.low, xlabel.high
        print "\t\tY:", ylabel.title, ylabel.low, ylabel.high
    else:
        pylab.savefig(filename)
    print "... done"


#generate('violin-e-open', generate_schelleng_force)
#generate('violin-e-open', generate_schelleng_velocity)
#generate('violin-e-open', generate_schelleng_finger_position)
#generate('violin-e-open', generate_accel)
#display('violin-e-open')

#generate('violin-e-open-2', generate_schelleng_force)
#display('violin-e-open-2')

#generate('violin-e-fourth')
#display('violin-e-fourth')

#generate('violin-g-open', generate_schelleng_force)
#generate('violin-g-open', generate_accel)
#display('violin-g-open')

#generate('cello-a-open', generate_schelleng_force)
#display('cello-a-open')

#generate('cello-d-open', generate_schelleng_force)
#display('cello-d-open')

#generate('cello-a-open', generate_schelleng_force)
#display('cello-a-open')

#generate('cello-g-open', generate_schelleng_force)
#display('cello-g-open')

#generate('cello-c-open', generate_schelleng_force)
#generate('cello-c-open', generate_schelleng_velocity)
#generate('cello-c-open', generate_accel)
#display('cello-c-open')

#generate('cello-c-open-2', generate_schelleng_force)
#display('cello-c-open-2')

#display_filename('/tmp/art/violin-e-open/coll.pickle')
#display_filename('/tmp/art/violin-e-open-96/coll.pickle')



#display_filename('violin-e-open-log.pickle', 'violin-e-open-log')
#display_filename('violin-e-log-2.pickle', 'violin-e-log-2')
#display_filename('violin-e-open.pickle', 'violin-e-open')

#display_filename('cello-a-open.pickle', 'cello-a-open')
#display_filename('cello-g-open.pickle', 'cello-g-open')
#display_filename('violin-e-fingers.pickle', 'violin-e-finger')
#display_filename('violin-e-fingers2.pickle', 'violin-e-fingers2')


#display_filename('violin-e-log-1.pickle', 'violin-e-log-1')
#display_filename('violin-e-log-2.pickle', 'violin-e-log-2')
#display_filename('cello-d-log-1.pickle', 'cello-d-log-1')
#display_filename('cello-c-log-1.pickle', 'cello-c-log-1')


### final set
display_filename('violin-e-massive-1.pickle', 'violin-e-massive-1')
display_filename('violin-e-massive-2.pickle', 'violin-e-massive-2')
display_filename('cello-a-massive.pickle', 'cello-a-massive')
display_filename('cello-c-massive.pickle', 'cello-c-massive')

#pylab.show()


