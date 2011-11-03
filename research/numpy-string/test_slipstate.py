#!/usr/bin/env python

import numpy
numpy.seterr(all='raise')
import pylab

from constants import T, L, d, pl, E, mu_s, mu_d, mu_v0
us = mu_s; ud = mu_d; v0 = mu_v0;
#from defs import FS


DIRNAME="out-bow-skip/"
import os
if not os.path.exists(DIRNAME):
    os.makedirs(DIRNAME)
#FS = 55000
FS = 66150

Y_MIN = -1.0
Y_MAX = 1.0
X_MIN = -1.0
X_MAX = 1.0

DV_range = numpy.linspace(X_MIN, X_MAX, 1000)
#F_b = 1.0
#v_b = 0.4
x0 = 0.12 * L
#x0 = 0.1 * L
x1 = 0
F_b = 0.25
v_b = 0.1

def phi(x, n):
    phivals = numpy.sqrt(2.0/L) * numpy.sin(n*numpy.pi*x/L)
    return phivals

N = 40
def try_FS(FS, color):
    print
    n = numpy.arange(1, N+1)
    dt = 1.0 / FS
    rn = 7.8 + 0.4*(n)  # hard-code E string

    I = numpy.pi * (d**4) / 64
    w0n = numpy.sqrt( (T/pl)*(n*numpy.pi/L)**2 + (E*I/pl)*(n*numpy.pi/L)**4 )
    wn = numpy.sqrt( w0n**2 - rn**2 )
    print "highest mode:", wn[-1] / (2*numpy.pi)

    X1n = (numpy.cos(wn*dt) + (rn/wn)*numpy.sin(wn*dt))*numpy.exp(-rn*dt)
    X2n = (1.0/wn) * numpy.sin(wn*dt)*numpy.exp(-rn*dt)
    X3n = (1.0 - X1n) / (pl*(w0n**2))

    Y1n = -(wn+(rn**2)/wn)*numpy.sin(wn*dt)*numpy.exp(-rn*dt)
    Y2n = (numpy.cos(wn*dt) - (rn/wn)*numpy.sin(wn*dt))*numpy.exp(-rn*dt)
    Y3n = -Y1n / (pl*w0n**2)
    if any( Y3n < 0):
        print "FS not sufficient for number of modes!"
        exit(1)


    ### bow pos
    phix0 = phi(x0, n)
    #print phix0
    phix1 = phi(x1, n)


    A00 = sum(X3n * phix0 * phix0)
    A01 = sum(X3n * phix0 * phix1)
    A10 = sum(X3n * phix1 * phix0)
    A11 = sum(X3n * phix1 * phix1)
    A10 = A10

    B00 = sum(Y3n * phix0 * phix0)
    B01 = sum(Y3n * phix0 * phix1)
    #B10 = sum(Y3n * phix1 * phix0)
    #B11 = sum(Y3n * phix1 * phix1)

    K1 = 1e6
    #L1 = -K0 / (A00*A11*K0*K1 - A01*A10*K0*K1 + A11*K1 + A00*K0 + 1.0)
    #D1 = -K1 / (A11*K1 + 1.0)
    #D2 = A10*D1
    #D3 = (A11*K1+1.0)*L1
    #D4 = -(A01*K1)*L1
    L1 = 1.0 / (B00)

    D1 = 1.0 * L1
    D5 = 0
    D6 = 0


    print "B00: %.3g" % B00
    #D5 = 0.318897
    #print "D5:\t%g\tD6:\t%g" % (D5, D6)


    ### friction curves
    y1h = 0.0

    def low_v0h():
        #v0h = (
        #    (D6*y1h + D5*(v_b + v0) - F_b*ud
        #        - 2*numpy.sqrt(D5*v0*F_b*(us-ud)))
        #    / D5)
        #v0h = (
        #    (D6*y1h + D5*(v_b+v0)
        #      - numpy.sqrt(D5*v0*F_b*(us-ud)))
        #    / D5)

        ### stick limit
        #v0h = -F_b*us*B00 + v_b
        #return v0h
        #over_sqrt = 1.0 / numpy.sqrt(D5*v0*F_b*(us-ud))
        #v0h = (y1h*D6/D5
        #    - 2*F_b*v0*over_sqrt*(us-ud)
        #    - F_b*ud/D5
        #    + v_b + v0
        #    )
        dv = v0 - numpy.sqrt(D1*v0*F_b*(us-ud)) / (D1)
        v0h = ((D1*((v0 - dv) * v_b + v0*dv - dv**2) + F_b*(ud*dv-us*v0))
            / ( D1*(v0-dv)))
        
        #v0h_maybe = (v_b*D1 + F_b *us) / (D1)
        #print "zzzzzzzzzzzzzzzzzzzzzzzzz MAYBE: ", v0h, v0h_maybe
        if dv >= 0:
            print "Can't find single low point for %i modes with FS=%i" % (
                N, FS)
            v0h = (D6*y1h + D5*v_b - F_b*us) / D5
        return v0h
    def high_v0h():
        v0h = F_b*us*B00 + v_b
        return v0h
    v0h_cands = [ low_v0h(), high_v0h() ]
    #y0dh_cands = [ high_v0h() ]
    #y0dh_cands = [ low_v0h(), low_v0h() ]



    def modal(dv, v0h):
        return D1 * (dv + v_b - v0h)

    def friction(dv):
        return F_b * (ud + (us-ud) / (1.0-dv/v0))
        #return F_b * (ud + (us-ud)*v0 / (v0-dv))

    for i, cand in enumerate(v0h_cands):
        m = modal(DV_range, cand)
        dv_tiny = numpy.array([ min(DV_range), max(DV_range)])
        m_tiny = numpy.array([ min(m), max(m)])

        data = numpy.vstack( (dv_tiny, m_tiny) ).transpose()
        numpy.savetxt( DIRNAME+"modal-%i-%i.txt" % (FS, i), data)

        pylab.plot(dv_tiny, m_tiny,
            label="%i Hz, time %i"% (FS, i),
            color=color)
    print "%i nodes: low, high\t%s" % (N, v0h_cands)
    bad_accel = v0h_cands[1] - v0h_cands[0]
    print "bad diff v0h:\t%.3g" % (bad_accel)
    print "low, high modal:\t%.3g\t%.3g" % (
        modal(-1, v0h_cands[0]), modal(1, v0h_cands[0]))
    print "low, high modal:\t%.3g\t%.3g" % (
        modal(-1, v0h_cands[1]), modal(1, v0h_cands[1]))

    low = v0h_cands[0]
    high = v0h_cands[1]
    print "copy&paste next line:"
    text = "%.4g %.4g %.4g %.4g" % (
        B00, low, high, high-low)
    print text

   
if True:
    def msw_friction(dv):
        if dv < 0:
            return F_b * (ud + (us-ud)*v0 / (v0-dv))
        else:
            return -F_b * (ud + (us-ud)*v0 / (v0+dv))
    msw_friction = numpy.vectorize(msw_friction)
    msw = msw_friction(DV_range)
    pylab.axhline(0, color="gray")
    pylab.plot(DV_range, msw,
        color="red")

    data = numpy.vstack( (DV_range, msw) ).transpose()
    numpy.savetxt( DIRNAME+"skips-friction-curve.txt", data)


#try_N(10, "cyan")
#try_N(20, "green")
try_FS(55000, "blue")
try_FS(66150, "purple")
try_FS(110000, "orange")
#try_N(36, "orange")
#try_N(70, "purple")

pylab.xlim([X_MIN, X_MAX])
pylab.ylim([Y_MIN, Y_MAX])
pylab.legend()
pylab.show()

