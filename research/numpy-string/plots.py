#!/usr/bin/env python 

import os.path
import sys

import numpy
import pylab
import scipy.fftpack
import scipy.signal

from defs import *
import defs

def write_positions(basename, displacements, disps_h,
        L):
    num_rows, num_columns = displacements.shape
    x = numpy.linspace(0, L, num_columns)

    def write_to(filename, values):
        out = open(filename, 'w')
        for i in range(PLOT_SAMPLE_MIN, PLOT_SAMPLE_MAX):
            if (i-PLOT_SAMPLE_MIN) % int(float(FS) / DISPLACEMENTS_SAMPLE_RATE) > 0:
                continue
            seconds = float(i) / FS
            out2 = open(filename.replace(".txt",
                    "-%i.txt" % (i-PLOT_SAMPLE_MIN)), 'w')
            for j in range(len(values[i])):
                out.write("%g %g %g\n" % (
                    seconds, x[j], values[i][j]))
                out2.write("%g %g %g\n" % (
                    1000*(seconds-0.1), x[j], values[i][j]))
            out2.close()
            out.write("\n")
        out.close()

    write_to(os.path.join(DATA_DIR,
        "%s-positions-actual.txt" % (basename))
        , displacements)
    #write_to(os.path.join(DATA_DIR,
    #    "%s-positions-hist.txt" % (basename))
    #    , disps_h)

def draw_positions(basename, displacements, disps_h,
        x0s, x1s, x2s, L, bowstates):
    ylim = numpy.max(numpy.abs(displacements[PLOT_SAMPLE_MIN:PLOT_SAMPLE_MAX]), axis=None)

    num_rows, num_columns = displacements.shape
    x = numpy.linspace(0, L, num_columns)
    
    for i in range(PLOT_SAMPLE_MIN, PLOT_SAMPLE_MAX):
        if (i-PLOT_SAMPLE_MIN) % int(float(FS) / DISPLACEMENTS_SAMPLE_RATE) > 0:
            continue
        seconds = float(i) / FS
        filename = os.path.join(DATA_DIR,
            "%s-%.6f.png" % (basename, seconds))
    
        pylab.figure()
        if PLOT_EXTRA_HARMONIC_LINES_AT_QUARTERS:
            pylab.axvline( 0.25*L, color='pink')
            pylab.axvline( 0.5*L, color='pink')
            pylab.axvline( 0.75*L, color='pink')

        pylab.axhline( 0, color='grey')

        pylab.plot(x, disps_h[i], color='blue', alpha=0.3)
        pylab.plot(x, displacements[i], color='blue')

        if bowstates[i] == 0: # 0 is stick, 1 and -1 are slip
            pylab.axvline( x0s[i], color='green', linewidth=2.0)
        else:
            pylab.axvline( x0s[i], color='green')
        pylab.axvline( x1s[i], color='orange')
        pylab.axvline( x2s[i], color='purple')
    
        pylab.xlim([0, L])
        pylab.ylim([-ylim, ylim])
        pylab.xlabel("Position along string (bridge at 0, nut at %.3f)" % L)
        pylab.ylabel("Displacement (m)")
        pylab.title("String at %.6f seconds, sample %0i" % (seconds, i))
        pylab.savefig(filename)
        pylab.close()

def plot_time_domain(dts, data, title):
    dts  = dts [PLOT_SAMPLE_MIN:PLOT_SAMPLE_MAX]
    data = data[PLOT_SAMPLE_MIN:PLOT_SAMPLE_MAX]
    pylab.figure()
    pylab.plot(dts, data, '-')
    pylab.xlabel("seconds")
    pylab.title(title + " time domain")

def plot_time_two(dts, data1, data2, title):
    dts   = dts [PLOT_SAMPLE_MIN:PLOT_SAMPLE_MAX]
    data1 = data1[PLOT_SAMPLE_MIN:PLOT_SAMPLE_MAX]
    data2 = data2[PLOT_SAMPLE_MIN:PLOT_SAMPLE_MAX]
    pylab.figure()
    pylab.plot(dts, data1, '-', label="first")
    pylab.plot(dts, data2, '-', label="second")
    pylab.xlabel("seconds")
    pylab.title(title + " time domain")
    pylab.legend()

    #pylab.plot(dts[:-1], data2[1:]-data[:1], label="delta")


 
def plot_time_fft(dtsorig, dataorig, title, basename):
    dts  = dtsorig [PLOT_SAMPLE_MIN:PLOT_SAMPLE_MAX]
    data = dataorig[PLOT_SAMPLE_MIN:PLOT_SAMPLE_MAX]

    dts_time  = dtsorig [PLOT_TIME_SAMPLE_MIN:PLOT_TIME_SAMPLE_MAX]
    data_time = dataorig[PLOT_TIME_SAMPLE_MIN:PLOT_TIME_SAMPLE_MAX]
    pylab.figure()
    pylab.subplot(211)
    pylab.plot(dts, data, '-')
    pylab.xlabel("seconds")
    pylab.title(title + " time domain")

    pylab.subplot(212)
    #datafft = dataorig
    datafft = data[:65536]  # reduce length if longer
    if not PLOT_FINAL_OUTPUT_FFT_NO_WINDOW:
        window = scipy.signal.get_window('blackmanharris', len(datafft))
    else:
        window = scipy.signal.get_window('boxcar', len(datafft))
    #print "len fft:", len(datafft)
    fft = scipy.fftpack.fft(datafft*window)[:len(datafft)/2+1]
    #fft = scipy.fftpack.fft(datafft)[:len(datafft)/2]
    #fft = fft[:-1] # remove nyquist bin
    try:
        #fft_db = 20*numpy.log10(abs(fft) / max(abs(fft)))
        fft_db = 20*numpy.log10(abs(fft) / len(fft))
    except:
        fft_db = numpy.zeros(len(fft))
    freqs = numpy.linspace(0, FS/2, len(datafft)/2)
    #freqs = freqs[:-1] # remove nyquist bin
    #pylab.figure()
    #pylab.plot(datafft*window)
    #pylab.show()

    if PLOT_MAX_FREQ > 0:
        low  = float(PLOT_MIN_FREQ) / (FS) * len(datafft)
        high = float(PLOT_MAX_FREQ) / (FS) * len(datafft)
        #print low, high
        freqs  = freqs [low:high]
        fft_db = fft_db[low:high]
        #pylab.xlim([PLOT_MIN_FREQ, PLOT_MAX_FREQ])
    pylab.plot(freqs, fft_db)

    pylab.title(title + " frequency magnitude")
    pylab.xlabel("frequency (Hz)")

    #dts = 1000*(dts - 0.1)
    #dts = dts-0.1
    #dts_time = dts_time-0.1
    data = numpy.vstack( (dts_time, data_time) ).transpose()
    filename = os.path.join(DATA_DIR,
        "%s-time-data.txt" % basename)
    if PLOT_FINAL_OUTPUT_TIME:
        numpy.savetxt(filename, data)
    if PLOT_FINAL_OUTPUT_FFT:
        data = numpy.vstack( (freqs, fft_db) ).transpose()
        filename = os.path.join(DATA_DIR,
            "%s-freqs-fftdb.txt" % basename)
        numpy.savetxt(filename, data)

    #filename = os.path.join(DATA_DIR,
    #    "%s-decay.wav" % basename)
    #scipy.io.wavfile.write(filename,
    #    FS, numpy.int16( SCALE_WAV_OUTPUT * datafft * (2**15) ))


    #freqs = numpy.linspace(0, FS/2, len(datafft)/2)
    #pylab.subplot(313)
    #pylab.plot(freqs, numpy.angle(fft))
    #pylab.title(title + " phase")
    #pylab.xlabel("frequency (Hz)")

    #if PLOT_MAX_FREQ > 0:
    #    pylab.xlim([0, PLOT_MAX_FREQ])

    # ironically, this command makes the spacing not as tight
    # (but avoids overlap) -- however, it's not present in my
    # version of pylab
    #pylab.tight_layout()


class Plots():
    def __init__(self, N, num_samples, L):
        self.sample = 0
        self.dts    = (1.0/FS) * numpy.arange(num_samples)
        self.L = L

        self.outs = numpy.empty(num_samples)
        self.x0s = numpy.empty(num_samples)
        self.x1s = numpy.empty(num_samples)
        self.x2s = numpy.empty(num_samples)
        self.F0s = numpy.empty(num_samples)
        self.F1s = numpy.empty(num_samples)
        self.F2s = numpy.empty(num_samples)
        self.y0s = numpy.empty(num_samples)
        self.v0s = numpy.empty(num_samples)
        self.v0hs = numpy.empty(num_samples)
        self.v1hs = numpy.empty(num_samples)
        self.v1s  = numpy.empty(num_samples)
        self.F_bridges  = numpy.empty(num_samples)
        self.F_nuts  = numpy.empty(num_samples)
        self.bowstates = numpy.empty(num_samples)

        self.ans  = numpy.empty( (num_samples, N) )
        self.adns = numpy.empty( (num_samples, N) )
        if PLOT_DISPLACEMENTS or WRITE_DISPLACEMENTS:
            self.disp_ps = numpy.empty( (num_samples, DISPLACEMENTS_ALONG_STRING) )
            self.disp_ps_h = numpy.empty( (num_samples, DISPLACEMENTS_ALONG_STRING) )
        
    def add_data(self,
            out,
            an, adn,
            x0, x1, x2,
            F0, F1, F2,
            y0,
            v0, v0h,
            v1, v1h,
            F_bridge, F_nut,
            disps, disps_h,
            bowstate,
        ):
        self.outs     [self.sample] = out
        self.ans      [self.sample] = an
        self.adns     [self.sample] = adn
        self.x0s      [self.sample] = x0
        self.x1s      [self.sample] = x1
        self.x2s      [self.sample] = x2
        self.F0s      [self.sample] = F0
        self.F1s      [self.sample] = F1
        self.F2s      [self.sample] = F2
        self.y0s      [self.sample] = y0
        self.v0hs     [self.sample] = v0h
        self.v0s      [self.sample] = v0
        self.v1s      [self.sample] = v1
        self.v1hs     [self.sample] = v1h
        self.F_bridges[self.sample] = F_bridge
        self.F_nuts   [self.sample] = F_nut
        self.bowstates[self.sample] = bowstate
        if PLOT_DISPLACEMENTS or WRITE_DISPLACEMENTS:
            self.disp_ps  [self.sample] = disps
            self.disp_ps_h[self.sample] = disps_h

        self.sample += 1

    def plot(self):
        if PLOT_FINAL_OUTPUT:
            plot_time_fft(self.dts, self.outs, "final output",
                "output")
        if PLOT_FORCES:
            if PLOT_FORCES_FFT:
                if not SINGLE_FINGER_FORCE:
                    plot_time_fft(self.dts, self.F0s, "bow F",
                        "F0")
                plot_time_fft(self.dts, self.F1s, "finger F1",
                    "F1")
                #plot_time_fft(self.dts, self.F2s, "finger F2")
            else:
                plot_time_domain(self.dts, self.F0s, "bow F")
                plot_time_domain(self.dts, self.F1s, "finger F1")
                #plot_time_domain(self.dts, self.F2s, "finger F2")
                #plot_time_two(self.dts, self.F1s, self.F2s, "fingers")
        if PLOT_MODE_DISPLACEMENTS:
            pylab.figure()
            dts = self.dts[PLOT_SAMPLE_MIN:PLOT_SAMPLE_MAX]
            dts = 1000*(dts - 0.1)
            for i in range(N):
                data = self.ans[:,i][PLOT_SAMPLE_MIN:PLOT_SAMPLE_MAX]
                pylab.plot(dts, data, '.-',
                    label="mode %i"%(i+1),
                    alpha=0.3)
                data = numpy.vstack( (dts, data) ).transpose()
                filename = "displacement-mode-%i.txt" % i
                numpy.savetxt(filename, data)
            pylab.xlabel("seconds")
            pylab.legend()
            pylab.title("Modal displacement")

        if PLOT_BOW_SLIPSTATES:
            dts = self.dts[PLOT_TIME_SAMPLE_MIN:PLOT_TIME_SAMPLE_MAX]
            data = self.bowstates[PLOT_TIME_SAMPLE_MIN:PLOT_TIME_SAMPLE_MAX]
            data = numpy.vstack( (dts, data) ).transpose()
            basename = os.path.basename(self.main_filename)
            filename = os.path.join(DATA_DIR,
                "%s-slipstates.txt" % basename)
            numpy.savetxt(filename, data)
            
            data = self.v0hs[PLOT_TIME_SAMPLE_MIN:PLOT_TIME_SAMPLE_MAX]
            data = numpy.vstack( (dts, data) ).transpose()
            basename = os.path.basename(self.main_filename)
            filename = os.path.join(DATA_DIR,
                "%s-v0hs.txt" % basename)
            numpy.savetxt(filename, data)

        if PLOT_BOW_COMBO:
            pylab.figure()
            deriv_v0hs = self.v0hs[1:]-self.v0hs[:-1]

            # I think this works because bow_velocity is constant?
            deriv_Dvs = self.v0s[1:] - self.v0s[:-1]

            #acc = deriv_v0hs
            #pylab.plot(self.dts[:-1], acc,
            #    color="green",
            #    label="accel (deriv of v0h)")
            #print "max abs derivative v0hs:\t%.2g" % (max(abs(acc)))
            #acc = acc[len(acc)*0.9:]
            #print "max abs derivative v0hs:\t%.2g" % (max(abs(acc)))

            pylab.plot(self.dts, self.v0hs,
                color="blue", alpha=0.3,
                label="v0h")
            pylab.plot(self.dts, self.v0s,
                color="blue",
                label="v0")
            pylab.plot(self.dts, self.bowstates,
                color="red",
                label="bowstates")
            pylab.plot(self.dts, self.v0s - defs.bow_velocity,
                color="green",
                label="Dv")
            pylab.plot(self.dts, self.F0s,
                color="purple",
                label="F0")
            pylab.xlabel("seconds")
            pylab.ylabel("stuff")

            pylab.legend(loc=3)
            pylab.title("Various bowing data")

            pylab.figure()
            #pylab.plot(self.dts[:-1], deriv_Dvs)
            pylab.plot(self.dts[:-1], deriv_v0hs)

        if PLOT_DISP_BOW:
            pylab.figure()
            pylab.plot(self.dts, self.y0s,
                color="blue",
                label="after external forces")
            pylab.xlabel("seconds")
            pylab.ylabel("displacement (m)")
            pylab.legend(loc=3)
            pylab.title("String displacement under bow")
        #if PLOT_BOW_STATES:
        if False:
            pylab.figure()
            pylab.plot(self.dts, self.bowstates,
                color="blue",
                label="bowstates")
            pylab.xlabel("seconds")
            pylab.ylabel("bow state")
            pylab.ylim([-1.2, 1.2])
            pylab.legend(loc=3)
            pylab.title("Bow states")

        if PLOT_VELOCITY_UNDER_FINGER:
            pylab.figure()
            pylab.plot(self.dts, self.v1hs, label="without external forces")
            pylab.plot(self.dts, self.v1s, label="after external forces")
            pylab.xlabel("seconds")
            pylab.ylabel("velocity (m/s)")
            pylab.legend()
            pylab.title("String velocity under finger")
    
        if PLOT_DISPLACEMENTS:
            basename = os.path.basename(self.main_filename)
            draw_positions(basename,
                self.disp_ps, self.disp_ps_h,
                self.x0s, self.x1s, self.x2s, self.L,
                self.bowstates)
        if WRITE_DISPLACEMENTS:
            basename = os.path.basename(self.main_filename)
            write_positions(basename,
                self.disp_ps, self.disp_ps_h,
                self.L)

        #print "y0dh_cands = [%.4f, %.4f, %.4f, %.4f]" % (
        #    min(self.v0hs), self.v0hs.mean(), 0, max(self.v0hs))

        if defs.PLOTS_SHOW:       
            pylab.show()

    def get_dts_F1(self):
        return self.dts, self.F1s

def main():
    filename = sys.argv[1]
    basename = os.path.splitext(os.path.basename(filename))[0]
    
    data = numpy.loadtxt(filename)
    
    seconds = data[:,0]
    displacements = data[:,1:]
    draw(basename, seconds, displacements)
    
if __name__ == "__main__":
    main()

