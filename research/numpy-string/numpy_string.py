#!/usr/bin/env python

import os
import numpy
numpy.seterr(all='raise')
numpy.seterr(under='ignore')
import random

from defs import *
import defs
import plots
import scipy.linalg

from constants import T, L, d, pl, E, mu_s, mu_d, mu_v0
from constants import rn as rn_const
import constants

DATA_DIR = os.path.join("data", defs.THESIS.replace(" ", "-"))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
plots.DATA_DIR = DATA_DIR


PLUCK_MAX_DISPLACEMENT = 0.005 # meters
PLUCK_MAX_VELOCITY = 0.1 # how quickly can the pluck finger move?
PLUCK_SAMPLES = 0 # defined lower, after getting FS

def thesis_save(text, values):
    filename = os.path.join(
        DATA_DIR,
        "%s-%s.txt" % (text, constants.which_string)
        )
    numpy.savetxt(filename, numpy.vstack( (
        [n for n in range(1, len(values)+1)], values)).transpose())


### conventions:
# variable name ending in a:
#   *0: the pluck
#   *1: the finger
#   *n: a vector of N modes
#   *s: a vector of time-varying data
#   *ns: a matrix of modal data over time.
#        Rows are time samples, columns are modes
#   *ps: a matrix of string displacements
#        Rows are time samples, columns are real-world points
#        along the string
#
# argh, sorry, I just noticed that here I've used
#   v1  = string velocity at point 1
# whereas in the #thesis I used
#   \dot{y}_1 = string velocity at point 1.
# if that's confusing I'll send an updated version


### setup additional constants
num_samples = 0
dt = 0
n = numpy.arange(1, defs.N+1)
def set_constants():
    global num_samples, X1n, X2n, X3n, Y1n, Y2n, Y3n, pc_bridge, wn
    global dt

    global FS, N, n
    FS = defs.FS # to get changes
    N = defs.N
    n = numpy.arange(1, defs.N+1)

    global PLUCK_SAMPLES
    PLUCK_SAMPLES = int(FS*0.1) # 100 ms pluck
    num_samples = int(SECONDS*FS)
    dt = 1.0 / FS
    
    I = numpy.pi * (d**4) / 64 # second moment of area of a circular cross-section
    
    w0n = numpy.sqrt( (T/pl)*((n*numpy.pi/L)**2) + (E*I/pl)*((n*numpy.pi/L)**4) )
    rn = rn_const[:N]
    wn = numpy.sqrt( w0n**2 - rn**2 )
    #print "w0n in Hz:", w0n / (2*numpy.pi)
    if wn[-1] / (2*numpy.pi) >= FS/2:
        print "ERROR: sampling rate not high enough for number of modes"
        print "wn / (2pi):\t", wn / (2*numpy.pi)
        print FS/2
        exit(1)
    
    #rn = 1000.0
    X1n = (numpy.cos(wn*dt) + (rn/wn)*numpy.sin(wn*dt))*numpy.exp(-rn*dt)
    #X1n = (numpy.cos(wn*dt) + (rn/wn)*numpy.sin(wn*dt))
    X2n = (1.0/wn) * numpy.sin(wn*dt)*numpy.exp(-rn*dt)
    X3n = (1.0 - X1n) / (pl*(w0n**2))
    if defs.WRITE_X3N_Y3N:
        thesis_save("X3n", X3n)
    
    Y1n = -(wn+(rn**2)/wn)*numpy.sin(wn*dt)*numpy.exp(-rn*dt)
    Y2n = (numpy.cos(wn*dt) - (rn/wn)*numpy.sin(wn*dt))*numpy.exp(-rn*dt)
    Y3n = -Y1n / (pl*w0n**2)

    #print "Y3n:", Y3n

    if defs.WRITE_X3N_Y3N:
        thesis_save("Y3n", Y3n)
    
    pc_bridge = numpy.sqrt(2.0/L) * (T*(n*numpy.pi/L) + E*I*(n*numpy.pi/L)**3)
set_constants()

# basis function
def phi(x):
    phivals = numpy.sqrt(2.0/L) * numpy.sin(n*numpy.pi*x/L)
    #if x == 0.5*L:
    #    phivals[1] = 0
    #    #print phivals[0], phivals[2]
    #    #exit(1)
    #if x == 1.0*L:
    #    phivals = numpy.zeros(N)
    #print "phi(%.3f) = %s" % (x, phivals)
    return phivals



class Violin():
    def __init__(self, num_samples = None):
        if num_samples is not None:
            self.plotting = plots.Plots(N, num_samples, L)
        ### simulation variables
        self.an = numpy.zeros(N)   # modal displacements
        self.adn = numpy.zeros(N)  # modal velocities; "d" is for "dot"

        # positions
        self.x0 = 0 # bow or pluck
        self.x1 = 0 # finger
        self.x2 = 0
        self.x3 = 0
        self.phix0 = phi(self.x0)
        self.phix1 = phi(self.x1)
        self.phix2 = phi(self.x2)
        self.phix3 = phi(self.x3)
        self.K0 = 0
        self.K1 = 0
        self.K2 = 0
        self.K3 = 0
        self.R0 = 0
        self.R1 = 0
        self.R3 = 0
        self.ypluck = 0
        self.plucks_left = False
        self.release = False

        self.x_finger = 0
        self.x_pluck = 0
        self.K_pluck = 0
        self.K_finger = 0
        self.R_pluck = 0
        self.R_finger = 0
        # bowing stuff
        self.Fb = False
        self.vb = 0
        self.bowstate = 0 # 0=stick, 1=slip

        self.debug_max_dv0h = 0
        self.debug_prev_dv = 0
        self.debug_prev_v0h = 0
        self.debug_dv = 0

        self.debug_print_state = False
        self.debug_tick = 0
        self.debug_plucks = 0
        self.debug_slips = 0

    def finger(self, x_finger, K, R):
        if x_finger == 1.0: 
            x_finger = 0.0
        if 0 < x_finger < 0.5:
            print "WARNING!  bad finger position.  re-think?"
            exit(1)
        #print "finger at x_finger", x_finger
        self.x_finger = x_finger*L
        self.K_finger = K
        self.R_finger = R

        self.x1 = self.x_finger
        self.K1 = self.K_finger
        self.R1 = self.R_finger

        if 0 < self.x_finger < L - defs.Wf:
            self.x2 = self.x_finger + defs.Wf
            self.K2 = self.K_finger
            self.R2 = self.R_finger

            self.x0 = self.x_finger + 0.5*defs.Wf
            self.K0 = self.K_finger
            self.R0 = self.R_finger
        else:
            self.x0 = 0
            self.K0 = 0
            self.R0 = 0
            self.x2 = 0
            self.K2 = 0
            self.R2 = 0

        if DOUBLE_FINGER_FORCE:
            self.x0 = self.x_finger + defs.Wf
            self.K0 = self.K_finger
            self.R0 = self.R_finger
            self.x2 = 0
            self.K2 = 0
            self.R2 = 0
        if TEST_BOW:
            self.x2 = 0 # disable
            self.K2 = 0
            self.R2 = 0

        self.phix0 = phi(self.x0)
        self.phix1 = phi(self.x1)
        self.phix2 = phi(self.x2)
        #print "finger x0 x1 x2:", self.x0, self.x1, self.x2
        self.calc_coefficients()

    def bow(self, x0, Fb, vb):
        #print "bow pos:", x0
        self.x0 = x0*L
        self.Fb = Fb
        self.vb = vb
        self.phix0 = phi(self.x0)
        self.phix1 = phi(self.x1)
        self.phix2 = phi(self.x2)
        self.calc_coefficients()

        dv_low = mu_v0 - (
            numpy.sqrt(self.Fb * mu_v0 * self.D1 * (mu_s - mu_d))
            / self.D1)
        dv_high = -mu_v0 + (
            numpy.sqrt(self.Fb * mu_v0 * self.D1 * (mu_s - mu_d))
            / self.D1)
        #print "zzzz min bow skipping"
        #print "dv_low, dv_high:\t%.3f\t%.3f" % (dv_low, dv_high)
        #print "dv_high - dv_low:\t%.3f" % (dv_high - dv_low)
        #exit(1)

        return


        #if self.Fb == 0:
        #    self.Fb = False
        #    self.pluck_stop()


        y1h = 0
        return
        upper_stable = (y1h*self.D2 + vb*self.D1 - Fb*mu_s) / self.D1
        lower_stable = (y1h*self.D2 + vb*self.D1 + Fb*mu_s) / self.D1
        upper_corner = ((y1h*self.D2 + vb*self.D1 - Fb*mu_s +
                self.D1*mu_v0) / self.D1
                - 2*abs( (numpy.sqrt(self.D1*mu_v0*self.Fb*(mu_s-mu_d)))
                    /self.D1 ))
        #print upper_corner, upper_stable
        Dv0h = lower_stable - min(upper_corner, upper_stable)
        #print "Dv0h: %.4f" % Dv0h
        #exit(1)

    def pluck(self, x_pluck, K, R):
        #print "pluck at x_pluck", x_pluck
        self.x_pluck = x_pluck*L
        self.K_pluck = K
        self.R_pluck = R

        self.x0 = self.x_pluck
        self.K0 = self.K_pluck
        self.R0 = self.R_pluck

        if 0 < self.x_pluck < L - defs.Wp:
            self.x2 = self.x_pluck + defs.Wp
            self.K2 = self.K_pluck
            self.R2 = self.R_pluck
            if FOUR_PLUCK_FORCES:
                self.x3 = self.x_finger + defs.Wf
                self.K3 = self.K_finger
                self.R3 = self.R_finger
                self.phix3 = phi(self.x3)
        else:
            self.x2 = 0
            self.K2 = 0
            self.R2 = 0
        if SINGLE_PLUCK_FORCE:
            self.x2 = 0
            self.x2 = 0
            self.K2 = 0

        #print "begin pluck"

        self.ypluck = 0
        self.plucks_left = PLUCK_SAMPLES
        self.Fb = False
        self.release = False

        self.phix0 = phi(self.x0)
        self.phix1 = phi(self.x1)
        self.phix2 = phi(self.x2)
        #print "pluck x0 x1 x2:", self.x0, self.x1, self.x2
        #print self.K1, self.R1
        self.calc_coefficients()

    def pluck_stop(self):
        self.plucks_left = False
        self.ypluck = 0
        self.release = True
        self.x3 = 0
        if 0 < self.x_finger < L - 0.01:
            # finger width, 1 cm
            self.x1 = self.x_finger
            self.x0 = self.x_finger + defs.Wf
            if RELEASE_FORCES_THREE:
                self.x0 = self.x_finger + defs.Wf
                self.x2 = self.x_finger + 0.5*defs.Wf
            else:
                self.x2 = 0
        else:
            self.x0 = 0
            self.x1 = 0
            self.x2 = 0

        if SINGLE_FINGER_FORCE:
            print "single finger force", SINGLE_FINGER_FORCE
            ## temp to generate plot in thesis
            self.x0 = 0
            self.x2 = 0
        if SINGLE_PLUCK_DOUBLE_FINGER_FORCE:
            self.x0 = 0
            self.x2 = self.x_finger + defs.Wf
            self.K2 = self.K_finger
            self.R2 = self.R_finger
        self.phix0 = phi(self.x0)
        self.phix1 = phi(self.x1)
        self.phix2 = phi(self.x2)
        self.phix3 = phi(self.x3)

        self.K0 = self.K_finger # fingering the string as a strong spring
        self.K1 = self.K_finger
        self.K2 = 0
        self.R0 = self.R_finger
        self.R1 = self.R_finger
        self.R2 = 0
        if RELEASE_FORCES_THREE:
            self.K2 = self.K_finger
            self.R2 = self.R_finger
        if SINGLE_PLUCK_DOUBLE_FINGER_FORCE:
            self.K0 = 0
            self.R0 = 0
        self.calc_coefficients()
        #self.debug_print_state = True

    def calc_coefficients(self):
        #print "positions x0 x1 x2 / L:", self.x0/L, self.x1/L, self.x2/L
        #print "  K0, K1, K2", self.K0, self.K1, self.K2
        #print "  R0, R1, R2", self.R0, self.R1, self.R2

        A00 = sum(X3n * self.phix0 * self.phix0)
        A01 = sum(X3n * self.phix0 * self.phix1)
        A02 = sum(X3n * self.phix0 * self.phix2)
        A10 = sum(X3n * self.phix1 * self.phix0)
        A11 = sum(X3n * self.phix1 * self.phix1)
        A12 = sum(X3n * self.phix1 * self.phix2)
        A22 = sum(X3n * self.phix2 * self.phix2)
        self.A00 = A00
        self.A01 = A01
        self.A10 = A10
        self.A11 = A11
        #print "A11:", A11

        B00 = sum(Y3n * self.phix0 * self.phix0)
        B01 = sum(Y3n * self.phix0 * self.phix1)
        B10 = sum(Y3n * self.phix1 * self.phix0)
        B11 = sum(Y3n * self.phix1 * self.phix1)
        B02 = sum(Y3n * self.phix0 * self.phix2)
        B12 = sum(Y3n * self.phix1 * self.phix2)
        B22 = sum(Y3n * self.phix2 * self.phix2)

        #K0 = 1e6
        #K1 = 1e6
        K0 = self.K0
        K1 = self.K1
        K2 = self.K2
        R0 = self.R0
        R1 = self.R1
        R2 = self.R2

        if FOUR_PLUCK_FORCES:
            A03 = sum(X3n * self.phix0 * self.phix3)
            A13 = sum(X3n * self.phix1 * self.phix3)
            A23 = sum(X3n * self.phix2 * self.phix3)
            A33 = sum(X3n * self.phix3 * self.phix3)
            B03 = sum(Y3n * self.phix0 * self.phix3)
            B13 = sum(Y3n * self.phix1 * self.phix3)
            B23 = sum(Y3n * self.phix2 * self.phix3)
            B33 = sum(Y3n * self.phix3 * self.phix3)
            K3 = self.K3
            R3 = self.R3
            lu_A = numpy.array([[
            B00*R0 + A00*K0 + 1, B01*R0 + A01*K0,     B02*R0 + A02*K0,     B03*R0 + A03*K0
            ],[
            B01*R1 + A01*K1,     B11*R1 + A11*K1 + 1, B12*R1 + A12*K1,     B13*R1 + A13*K1
            ],[
            B02*R2 + A02*K2,     B12*R2 + A12*K2,     B22*R2 + A22*K2 + 1, B23*R2 + A23*K2
            ],[
            B03*R3 + A03*K3,     B13*R3 + A13*K3,     B23*R3 + A23*K3,     B33*R3 + A33*K3
            ]])

        else:
            lu_A = numpy.array([[
            B00*R0 + A00*K0 + 1, B01*R0 + A01*K0,     B02*R0 + A02*K0,
            ],[
            B01*R1 + A01*K1,     B11*R1 + A11*K1 + 1, B12*R1 + A12*K1,
            ],[
            B02*R2 + A02*K2,     B12*R2 + A12*K2,     B22*R2 + A22*K2 + 1,
            ]])
        self.lu_A_LU = scipy.linalg.lu_factor(lu_A)

        L1old = -K0 / (A00*A11*K0*K1 - A01*A10*K0*K1 + A11*K1 + A00*K0 + 1.0)
        self.D1old = -K1 / (A11*K1 + 1.0)
        self.D2old = A10*self.D1old
        self.D3old = (A11*K1+1.0)*L1old
        self.D4old = -(A01*K1)*L1old
        #print "Ds 1-4"
        #print self.D1old
        #print self.D2old
        #print self.D3old
        #print self.D4old

        #print '----'
        #print self.phix0
        #print self.phix1
        #print self.x1
        #print "a10, a11:", A10, A11
        #print "b00, b01:", B00, B01
        #print "a11 b00:", A11*B00
        #print "a10 b01:", A10*B01
        #exit(1)
        #print A11*B00 > A10*B01
        #print "b00:", B00
        self.debug_A11 = A11
        self.debug_A10 = A10
        self.debug_B00 = B00
        self.debug_B01 = B01
        self.debug_A11_fake = sum(self.phix1 * self.phix1)
        self.debug_B00_fake = sum(self.phix0 * self.phix0)
        self.debug_A01_fake = sum(self.phix0 * self.phix1)

        try:
            L1 = 1.0 / (
              R1*(B00*B11 - B01*B10) + K1*(A11*B00 - A10*B01) + B00)
        except:
            L1 = 0
        #print "L1 parts:", R1*(B00*B11 - B01*B10), K1*(A11*B00 - A10*B01), B00

        self.D1 = (B11*R1 + K1*A11 + 1)*L1
        self.D2 = B01 * K1 * L1
        self.D3 = B01 * R1 * L1
        try:
            self.D4 = 1.0 / (2*self.D1)
        except:
            self.D4 = 0
        #print "D1:\t%g\tD2:\t%g" % (self.D1, self.D2)
        #print "L1, D1, D2, D3, D4"
        #print L1, self.D1, self.D2, self.D3, self.D4
        #print '-----'

        L2 = -1.0 / (B11*R1 + A11*K1 + 1.0)
        self.D5 = (B10*R1 + A10*K1) * L2
        self.D6 = R1 * L2
        self.D7 = K1 * L2


        ### new 2-force release
        R_FINGER = self.R_finger
        K_FINGER = self.K_finger

        self.M00 = A00*K_FINGER + B00*R_FINGER + 1
        self.M01 = A01*K_FINGER + B01*R_FINGER
        self.M11 = A11*K_FINGER + B11*R_FINGER + 1
        #print self.M00, self.M01, self.M11

        #L3 = -1.0 / (
        #    1.0
        #    + R_FINGER*R_FINGER * (B00*B11 - B01*B01)
        #    + K_FINGER*K_FINGER * (A00*A11 - A01*A01)
        #    + K_FINGER*R_FINGER * (A00*B11 + A11*B00 - 2.0*A01*B01)
        #    + K_FINGER * (A11 + A00)
        #    + R_FINGER * (B11 + B00)
        #    )
        #self.D8 = -1.0 / (K_FINGER*A00 + R_FINGER*B00 + 1.0)
        #self.D9 = (K_FINGER*A01 + R_FINGER*B01) * self.D8
        #self.D10 = (R_FINGER*B01 + K_FINGER*A01) * L3
        #self.D11 = -(R_FINGER*B00 + K_FINGER*A00 + 1.0) * L3
        L3 = 1.0 / (
            self.M00 * self.M11 - self.M01**2
            )
        self.D8 = -1.0 / self.M00
        self.D9 = -self.M01 / self.M00
        self.D10 = self.M01 * L3
        self.D11 = -self.M00 * L3
        #print L3, self.D8, self.D9, self.D10, self.D11



        L6 = -K2 / (A22*K1 + 1)
        L7 = -K1 / ( ((A11*A22-A12**2)*K1 + A22*K2) + A11*K1 + 1 )
        L9 = -K0 / (
            ((((A00*A11-A01**2)*A22 - A00*A12**2 + 2*A01*A02*A12
              -A02**2*A11)*K0 + A11*A22 - A12**2)*K1
              + (A00*A22 - A02**2)*K0 + A22)*K2
            + ((A00*A11 - A02**2)*K0 + A11)*K1
            + A00*K0+1)
        self.P1 = L9*(((A11*A22 - A12**2)*K1 + A22)*K2 + A11*K1 + 1)
        self.P2 = L9*K1*((A02*A12 - A01*A22)*K2 - A01)
        self.P3 = L9*K2*((A01*A12 - A02*A11)*K1 - A02)
        self.P4 = L7*((A02*A12 - A01*A22)*K2 - A01)
        self.P5 = L7*(A22*K2 + 1)
        self.P6 = L7*(-A12*K2)
        self.P7 = L6*A02
        self.P8 = L6*A12
        self.P9 = L6

        #print self.P1, self.P2, self.P3
        #print self.P4, self.P5, self.P6
        #print self.P7, self.P8, self.P9
        # for fingered plucks
        #self.A = numpy.empty( (2,2) )
        #self.A[0][0] = 1.0 + self.K0 * sum(X3n * self.phix0 * self.phix0)
        #self.A[0][1] =       self.K0 * sum(X3n * self.phix0 * self.phix1)
        #self.A[1][0] =       self.K1 * sum(X3n * self.phix1 * self.phix0)
        #self.A[1][1] = 1.0 + self.K1 * sum(X3n * self.phix1 * self.phix1)
        ## for open-string plucks
        #self.A00only = -self.K0 / (
        #    1.0 + self.K0 * sum(X3n * self.phix0 * self.phix0))
        # for bowing
        #A01 = sum(X3n * self.phix0 * self.phix1)
        #A11 = sum(X3n * self.phix1 * self.phix1)

    def tick_release(self, y0h, y1h, v0h, v1h):
        K_FINGER = self.K_finger
        R_FINGER = self.R_finger
        ans0 = (K_FINGER*y0h + R_FINGER*v0h)
        ans1 = (K_FINGER*y1h + R_FINGER*v1h)

        F1 = ans0 * self.D10 + ans1 * self.D11
        F0 = ans0 * self.D8 + F1 * self.D9
        #print F0, F1
        #F1 = (self.M00 * ans0 - self.M01 * ans1) / (
        #    self.M00 * self.M11 - self.M01**2)
        #F0 = ans0 / self.M00 - (self.M01 / self.M00) * F1
        return F0, F1, 0, 0

    def calc_pluck(self, y0h, y1h, y2h, y3h, v0h, v1h, v2h, v3h):
        if self.release and not RELEASE_FORCES_THREE:
            return self.tick_release(y0h, y1h, v0h, v1h)
        #if self.x1 == 0:   # open string
        #    F0 = self.A00only * (y0h - self.ypluck)
        #    return F0, 0
        # finger on string
        #B = numpy.array([-self.K0 * (y0h - self.ypluck), -self.K1*y1h])
        #x = numpy.linalg.solve(self.A, B)
        y0d = self.ypluck
        y1d = 0
        y2d = self.ypluck
        if FOUR_PLUCK_FORCES:
            y3d = 0
            lu_B = numpy.array([[
            -v0h * self.R0 - (y0h-y0d) * self.K0,
            ],[
            -v1h * self.R1 - (y1h-y1d) * self.K1,
            ],[
            -v2h * self.R2 - (y2h-y2d) * self.K2,
            ],[
            -v3h * self.R3 - (y3h-y3d) * self.K3,
            ]])
        else:
            lu_B = numpy.array([[
            -v0h * self.R0 - (y0h-y0d) * self.K0,
            ],[
            -v1h * self.R1 - (y1h-y1d) * self.K1,
            ],[
            -v2h * self.R2 - (y2h-y2d) * self.K2,
            ]])

        x = scipy.linalg.lu_solve(self.lu_A_LU, lu_B)
        F0 = x[0]
        F1 = x[1]
        F2 = x[2]
        if FOUR_PLUCK_FORCES:
            return F0, F1, F2, x[3]
        else:
            return F0, F1, F2, 0
        #v0d = (self.ypluck - y0h) / dt
        #print self.D3old, self.D4old
        #print self.D1old, self.D2old
        #print "y0h, y1h:", y0h, y1h
        #if DOUBLE_FINGER_FORCE:
        #    F0 = self.D3old*(y0h-self.ypluck) + self.D4old*(y1h)
            ### to generate a plot for the thesis
            #if self.debug_tick == 0:
            #    F0 = 0.01
            #else:
            #    F0 = 0
        #    F1 = self.D1old*(y1h) + self.D2old*F0
        #    return F0, F1, 0

        #return F0, F1, 0
        #if INFINITE_SPRING:
        #    # thesis experiment: infinitely strong F1
        #    F1 = -y1h / self.A11
        #print F0, F1
        #if self.ypluck > 0:
        #    exit(1)

        F0 = self.P1 * (y0h-self.ypluck) + self.P2*y1h + self.P3*(y2h-self.ypluck)
        #if F0 < 0:
        #    F0 = 0
        F1 = self.P5 * y1h + self.P6 * (y2h-self.ypluck) + self.P4*F0
        F2 = self.P9 * (y2h - self.ypluck) + self.P7 * F0 + self.P8 * F1
        #print self.ypluck
        #print F0, F1, F2
        return F0, F1, F2


    def calc_bow_force(self, y1h, v1h, v0h, dv):
        F0 = self.D1*(self.vb + dv - v0h) + self.D2*y1h + self.D3*v1h
        #print self.debug_tick, dv
        return F0

    def calc_bow_slip_negative(self, y1h, v1h, v0h):
        uN = 1.0 - defs.A_noise*random.random()
        mu_e = uN * mu_v0

        c1 = -self.D1 * (self.vb - v0h - mu_e) - self.D2*y1h - self.D3*v1h + self.Fb*mu_d
        c0 = mu_e * (self.D2*y1h + self.D1*(self.vb - v0h) + self.D3*v1h - self.Fb*mu_s)
        Delta = c1**2 + 4.0*c0*self.D1
        if Delta >= 0:
            dv = self.D4 * (c1 - numpy.sqrt(Delta))
            #c2 = -self.D1
            #dv_old = min(
            #    (-c1 - numpy.sqrt( c1**2 - 4*c0*c2 )) / (2*c2),
            #    (-c1 + numpy.sqrt( c1**2 - 4*c0*c2 )) / (2*c2))
            #print dv - dv_old
            if dv < 0:
                F0 = self.calc_bow_force(y1h, v1h, v0h, dv)
                if F0 < 0:
                    print "panic neg"
                    return None
                return F0
        return None

    def calc_bow_slip_positive(self, y1h, v1h, v0h):
        uN = 1.0 - defs.A_noise*random.random()
        mu_e = uN * mu_v0

        c1 = self.D1 *(self.vb - v0h + mu_e) + self.D2*y1h + self.D3*v1h + self.Fb*mu_d
        c0 = mu_e * (self.D2*y1h + self.D1*(self.vb - v0h) + self.D3*v1h + self.Fb*mu_s)

        Delta = c1**2 - 4.0*c0*self.D1
        if Delta >= 0:
            dv = self.D4 * (-c1 + numpy.sqrt(Delta))
            #c2 = self.D1
            #dv_old = max(
            #    (-c1 - numpy.sqrt( c1**2 - 4*c0*c2 )) / (2*c2),
            #    (-c1 + numpy.sqrt( c1**2 - 4*c0*c2 )) / (2*c2))
            #print dv - dv_old
            if dv > 0:
                F0 = self.calc_bow_force(y1h, v1h, v0h, dv)
                if F0 > 0:
                    print "panic pos"
                    return None
                return F0
        return None


    def calc_bow(self, y1h, v1h, v0h):
        #print '-----  bow state', self.bowstate
        #if self.bowstate > 0:
            #print "positive bowstate"
            #return None
        if self.bowstate == 0:
            F0 = self.calc_bow_force(y1h, v1h, v0h, 0)
            if abs(F0) > mu_s * self.Fb:
                #print "cannot stable:", F0, mu_s*self.Fb
                if v0h < self.vb:
                    # try negative
                    F0 = self.calc_bow_slip_negative(y1h, v1h, v0h)
                    if F0 is not None:
                        self.bowstate = -1
                        return F0
                elif v0h > self.vb:
                    if NO_POSITIVE_SLIPPING:
                        return F0
                    # try positive
                    F0 = self.calc_bow_slip_positive(y1h, v1h, v0h)
                    if F0 is not None:
                        self.bowstate = 1
                        return F0
                print "panic stick no longer"
                return None
                return 0
            else:
                self.dv = 0
                return F0
        elif self.bowstate == -1:
            F0 = self.calc_bow_slip_negative(y1h, v1h, v0h)
            if F0 is None:
                F0 = self.calc_bow_force(y1h, v1h, v0h, 0)
                if NO_POSITIVE_SLIPPING:
                    self.bowstate = 0
                    return F0
                if abs(F0) < mu_s * self.Fb:
                    self.bowstate = 0
                else:
                    if NO_SLIPPING_SKIPS:
                        print "stay positive"
                        self.bowstate = 0
                        return F0
                    self.debug_slips += 1
                    print "skip warn -1"
                    #print v0h, F0
                    #print "sample:", self.debug_tick
                    #print "seconds:", self.debug_tick / float(FS)
                    #return None
                    F0 = self.calc_bow_slip_positive(y1h, v1h, v0h)
                    #print F0
                    if F0 is not None:
                        self.bowstate = 1
                        return F0
                    print "panic -1"
                    return None
                return F0
            return F0
        elif self.bowstate == 1:
            F0 = self.calc_bow_slip_positive(y1h, v1h, v0h)
            if F0 is None:
                F0 = self.calc_bow_force(y1h, v1h, v0h, 0)
                if abs(F0) < mu_s * self.Fb:
                    self.bowstate = 0
                else:
                    if NO_SLIPPING_SKIPS:
                        print "stay positive"
                        self.bowstate = 0
                        return F0
                    self.debug_slips += 1
                    print "skip warn 1"
                    #print mu_s, self.Fb, mu_s*self.Fb
                    #print v0h, F0
                    #print "sample:", self.debug_tick
                    #print "seconds:", self.debug_tick / float(FS)
                    #return None
                    F0 = self.calc_bow_slip_negative(y1h, v1h, v0h)
                    if F0 is not None:
                        self.bowstate = -1
                        return F0
                    return None
                    print "panic 1"
                    return 0
                return F0
            return F0
        else:
            print "really bad"
            exit(1)

    def calc_forces(self, y0h, y1h, y2h, y3h, v0h, v1h, v2h, v3h):
        """ returns F0 and F1.
            TODO: add bow capability; right now it just does plucks
        """
        if self.plucks_left is not False:
            return self.calc_pluck(y0h, y1h, y2h, y3h, v0h, v1h, v2h, v3h)
        elif self.Fb is not False:
            F0 = self.calc_bow(y1h, v1h, v0h)
            if F0 is None:
                print "panic something wrong calc_forces"
                return None, None
            F1 = self.D5*F0 + self.D6*v1h + self.D7*y1h
            return F0, F1, 0, 0
        else:
            if INFINITE_SPRING:
                # thesis experiment: infinitely strong F1
                F0 = 0.0
                F1 = -y1h / self.A11
                F2 = 0.0
            else:
                #F0 = self.D3old*(y0h) + self.D4old*(y1h)
                #F1 = self.D1old*(y1h) + self.D2old*F0
                return self.calc_pluck(y0h, y1h, y2h, y3h, v0h, v1h, v2h, v3h)
            return F0, F1, F2, 0

    def update_pluck_pull(self):
        self.plucks_left -= 1
        #DAMPEN_SAMPLES = PLUCK_SAMPLES - PLUCK_SAMPLES/2
        #DAMPEN_SAMPLES = PLUCK_SAMPLES
        #NUM_STEPS = 19
        #if (self.plucks_left - DAMPEN_SAMPLES) % int(DAMPEN_SAMPLES / (NUM_STEPS+1)) == 0:
            #self.K0 *= (K0_FINAL / K0_INIT) ** (1.0 / (DAMPEN_SAMPLES))
            #if self.plucks_left > PLUCK_SAMPLES - DAMPEN_SAMPLES:
            #    self.K0 *= (K0_FINAL / K0_INIT) ** (1.0 / (NUM_STEPS))
            #    #self.K0 += (K0_FINAL - K0_INIT) * (1.0 / (NUM_STEPS))
            #    self.K2 = self.K0
            #    print "k0:", self.K0, self.plucks_left
            #    self.calc_coefficients()
        #    pass
        #elif self.plucks_left == DAMPEN_SAMPLES:
        #    self.K0 = K0_FINAL
        #    if self.x1 > 0:
        #        self.x2 = self.x1 + 0.01
        #    else:
        #        self.x2 = 0
        #    self.phix2 = phi(self.x2)
        #    #print self.K0
        #    self.calc_coefficients()
        #if False:
        #    pass
        if self.plucks_left == 0:
            self.debug_plucks += 1
            self.pluck_stop()
        elif self.ypluck < PLUCK_MAX_DISPLACEMENT:
            #if self.debug_plucks > 0:
            #    return
            # find velocity
            dyp = (PLUCK_MAX_DISPLACEMENT - self.ypluck)
            vel_yp = dyp / dt
            if vel_yp > PLUCK_MAX_VELOCITY:
                vel_yp = PLUCK_MAX_VELOCITY
            # update "spring at rest" position
            self.ypluck += vel_yp * dt
        else:
            pass
        #print self.plucks_left, self.ypluck

    def log_for_plot(self, F_bridge, F0, F1, F2, ahn, ahdn):
        ### log data for plotting
        v0h = sum(self.phix0*ahdn)
        y0 = sum(self.phix0*self.an)
        v0 = sum(self.phix0*self.adn)
        v1 = sum(self.phix1*self.adn)
        def get_disps():
            disps = numpy.empty( DISPLACEMENTS_ALONG_STRING )
            disps_h = numpy.empty( DISPLACEMENTS_ALONG_STRING )
            xs = numpy.linspace(0, L, DISPLACEMENTS_ALONG_STRING)
            for i, x in enumerate(xs):
                phix = phi(x)
                y = sum(phix * self.an)
                disps[i] = y
                yh = sum(phix * ahn)
                disps_h[i] = yh
            return disps, disps_h
        def extra_write(filename, values, seconds):
            filename = os.path.join(
                DATA_DIR, filename)
            out = open(filename, 'w')
            for j in range(len(values)):
                x = L * float(j) / (len(values)-1)
                out.write("%g %g %g\n" % (
                    seconds, x, values[j]))
            out.close()

        if (WRITE_DISPLACEMENTS_EXTRA and (
                self.debug_tick == 1 or
                self.debug_tick == PLUCK_SAMPLES)):
            disps, disps_h = get_disps()
            #import pylab
            #pylab.plot(disps)
            #pylab.show()
            if self.debug_tick == 1:
                #extra_write("pluck-begin-hist.txt", disps_h, 0)
                extra_write("pluck-begin-actual.txt", disps, 0)
            else:
                #extra_write("pluck-release-hist.txt", disps_h,
                #    float(PLUCK_SAMPLES)/FS)
                extra_write("pluck-release-actual.txt", disps,
                    float(PLUCK_SAMPLES)/FS)

        if ((PLOT_DISPLACEMENTS or WRITE_DISPLACEMENTS)
                and (PLOT_SAMPLE_MIN <= self.debug_tick
                    <= PLOT_SAMPLE_MAX)):
            disps, disps_h = get_disps()
        else:
            disps = None
            disps_h = None
    
        self.plotting.add_data(
            out = F_bridge,
            an = self.an, adn = self.adn,
            x0 = self.x0, x1 = self.x1, x2 = self.x2,
            F0 = F0, F1 = F1, F2 = F2,
            y0 = y0,
            v0 = v0, v0h = v0h,
            v1 = v1, v1h = 0,
            #v1 = v1, v1h = v1h,
            #F_bridge = F_bridge, F_nut = F_nut,
            F_bridge = F_bridge, F_nut = 0,
            disps = disps, disps_h = disps_h,
            bowstate = self.bowstate
            )


    def tick(self):
        """ advance time with previously-given actions """
        # "hands-free" values: how would the string behave if
        # there were no external forces
        ahn  = X1n*self.an + X2n*self.adn
        adhn = Y1n*self.an + Y2n*self.adn
    

        #print "D1:\t%g\tD2:\t%g" % (self.D1, self.D2)
        #print '-----'
        #exit(1)

        # what would be the displacements at positions x0 and x1
        # if there were no external forces?
        y0h = sum(self.phix0 * ahn)
        y1h = sum(self.phix1 * ahn)
        y2h = sum(self.phix2 * ahn)
        y3h = sum(self.phix3 * ahn)
        v0h = sum(self.phix0 * adhn)
        v1h = sum(self.phix1 * adhn)
        v2h = sum(self.phix2 * adhn)
        v3h = sum(self.phix3 * adhn)

        #print "v0h:\t", v0h, "y1h:\t", y1h
        # external forces at positions x0 and x1
        F0, F1, F2, F3 = self.calc_forces(y0h, y1h, y2h, y3h, v0h, v1h, v2h, v3h)
        #print F0, F1, F2
        #if F0 is None:
        #    return None

        # modal effects of external forces F0 and F1
        #exit(1)
        try:
            fn = self.phix0*F0 + self.phix1*F1 + self.phix2*F2 + self.phix3*F3
        except Exception as e:
            print F0, F1
            print self.phix0
            print self.phix1
            print "bail"
            raise (e)
            return None
            exit(1)
    
        # update string behaviour based on external forces
        self.an  = ahn  + X3n*fn
        self.adn = adhn + Y3n*fn

        #print "an:", self.an
        #print "adn:", self.adn
    
        # output of model for wav file
        F_bridge = sum(self.an * pc_bridge)


        if PLOTS:
            self.log_for_plot(F_bridge, F0, F1, F2, ahn, adhn)

        ### testing stick-skip
        #if self.debug_prev_dv * self.dv < 0:
        #    # change of sign
        #    dv0h = v0h - self.debug_prev_v0h
        #    if self.debug_max_dv0h < dv0h:
        #        self.debug_max_dv0h = dv0h
        #self.debug_prev_dv = self.dv
        dv0h = v0h - self.debug_prev_v0h
        if self.debug_max_dv0h < abs(dv0h):
            #print "new max: num_sample, value", self.debug_tick, abs(dv0h)
            #print self.debug_prev_v0h, v0h
            self.debug_max_dv0h = abs(dv0h)
        self.debug_prev_v0h = v0h


        # must be after the plots, else inaccurate graphics!
        if self.ypluck is not False:
            if self.plucks_left > 0:
                self.update_pluck_pull()
        self.debug_tick += 1
        #if self.debug_tick > 2:
        #    exit(1)
        if self.debug_print_state:
            print "an:\t", self.an
            print "adn:\t", self.adn
            self.debug_print_state = False

        return F_bridge


