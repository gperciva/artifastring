#!/usr/bin/env python

import sys

sys.path.append('../../build/swig')
sys.path.append('../../build/.libs')

sys.path.append('../shared/')
import math
import os
import datetime
import time
import pickle

import artifastring_instrument
import monowav

import numpy
import pylab
import scipy.stats
import scipy.fftpack

import random
import aubio.aubiowrapper

import scipy.io.wavfile

import expected_frequencies
import published_constants
import available_instruments

import cutoff

if not os.path.exists("pc-consts/"):
    os.makedirs("pc-consts")

#import arff
PAUSES = False

SHORT_DECAYS = 40

WINDOWSIZE = 1024
HOPSIZE = 512
TEST_SECONDS = 1.0
SAVE_DIRNAME = "pc-consts"

CUTOFF_ORIG = 1e-6

global_count = 0

# higher values are more noisy, lower values are more "spiky"
#MAX_SPECTRAL_FLATNESS = 0.01
MAX_SPECTRAL_FLATNESS = 0.5

NUM_PITCH_AVERAGE = 5

# this is a bit messed up to avoid an unfortunate newline
PC_CONSTS_FORMAT = """            %(T).1f, // T
            %(L).3f, // l
            %(d).2e, // d
            %(pl).2e, // pl
            %(E).2e, // E
            %(mu_s).3f, // static friction
            %(mu_d).3f, // dynamic friction
            %(v0).3f, // friction curve steepness
            %(cutoff).4g, // insignificant string vibrations
"""
# not used any more
EXTRA_IFDEF_N = """#ifdef RESEARCH
            %i, // number of modes N
#endif
"""

TABLE_ROW_OVERALL_FORMAT = "%s-%s-%s&%s"
TABLE_ROW_DATA_FORMAT = "%(T).1f&%(L).3f&%(d).2e&%(pl).2e&%(E).2e&%(mu_s).3f&%(mu_d).3f&%(v0).3f&%(cutoff).3g"

import inspect
def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.ismethod(value):
            pr[name] = value
    return pr

class Inst():
    def __init__(self, inst_num, inst_text, inst_num_text):
        self.pitch_obj = aubio.aubiowrapper.new_aubio_pitchdetection(
            WINDOWSIZE, HOPSIZE, 1,
            artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE,
            #aubio.aubiowrapper.aubio_pitch_yin,
            aubio.aubiowrapper.aubio_pitch_yinfft,
            aubio.aubiowrapper.aubio_pitchm_freq,
            )
        self.fvec = aubio.aubiowrapper.new_fvec(HOPSIZE, 1)
        self.vln = artifastring_instrument.ArtifastringInstrument(inst_num)
        self.audio_out_buf = numpy.empty(HOPSIZE, dtype=numpy.int16)
        self.force_out_buf = numpy.empty(HOPSIZE/4, dtype=numpy.int16)

        self.inst_text = inst_text
        self.inst_num_text = inst_num_text

        # icky!
        self.friction = {}

        self.pick_new_friction()
        self.pick_new_length()

        #self.attempts = []

    def save_consts(self, st, st_text):
        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        if not os.path.exists(SAVE_DIRNAME):
            os.makedirs(SAVE_DIRNAME)
        basename = os.path.join(SAVE_DIRNAME, date)
        while os.path.exists(basename+".txt"):
            time.sleep(1)
            date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            basename = os.path.join(SAVE_DIRNAME, date)
        self.write_constants(st, st_text)
        #self.test_bow(basename, 1.0)

    def get_modes(self, st, st_text):
        consts_basename = "%s-%s-%s" % (
            self.inst_text, st_text, self.inst_num_text)
        decay_pickle_filename = os.path.join(
            "../mode-detect/out/", consts_basename + ".mode-decays.pickle")
        pickle_file = open(decay_pickle_filename, 'rb')
        decays = pickle.load(pickle_file)
        pickle_file.close()
        return decays

    def get_constants_text(self, st, st_text):
        decays = self.get_modes(st, st_text)

        #filename = os.path.join('pc-consts', consts_basename + ".h")
        #out = open(filename, 'w')
        text = ""
        pc = self.vln.get_physical_constants(st)
        p = props(pc)
        text += " {   // %s %s %s\n" % (
            self.inst_text, st_text, self.inst_num_text)
        text += str(PC_CONSTS_FORMAT % p)

        text += "            // decays\n"
        text += "            // these were calculated by mode-detect/all-modes.py\n"
        text += "            {\n"
        decays = decays[:SHORT_DECAYS]
        for i in range(len(decays)):
            if i%4 == 0:
                text += "                "
            text += "%.3e," % decays[i]
            if i < len(decays)-1:
                if i%4 == 3:
                    #out.write("\n")
                    text += "\n"
                else:
                    text += " "
        text += "\n"
        text += "            },\n"
        #text += EXTRA_IFDEF_N % SHORT_DECAYS
        text += "        },"

        row = TABLE_ROW_OVERALL_FORMAT % (
            self.inst_text, st_text, self.inst_num_text,
            str(TABLE_ROW_DATA_FORMAT % p))

        return text, row

    def pick_new_constants(self, st, st_text, f0, B, L, d):
        decays = self.get_modes(st, st_text)

        pc_ideal = dict(published_constants.PHYSICAL_CONSTANT_RANGES[self.inst_text][st_text])
        #print pc_ideal
        #exit(1)
        pc = self.vln.get_physical_constants(st)


        ### update friction
        friction = dict(self.friction_init)
        for key in self.friction:
            friction[key] *= random.uniform(0.95, 1.05)
        pc.mu_s = friction['s']
        pc.mu_d = friction['d']
        pc.v0 = friction['v0']
        self.friction = friction

        ### length
        # do first, so it can be used in the tension calculation
        pc.L = self.L_init
        pc_ideal['L'] = [L*0.99, L*1.01]
        pc_ideal['d'] = [d*0.9, d*1.1]
        #print pc_ideal
        ### extend range of constants
        T = pc_ideal['T']
        #print T
        pc_ideal['T'] = [T[0]*0.75, T[1]*1.25]
        #print pc_ideal['T']
        #exit(1)
        pl = pc_ideal['pl']
        pc_ideal['pl'] = [pl[0]*0.75, pl[1]*1.25]

        for key in pc_ideal:
            low, high = pc_ideal[key]
            new_value = random.uniform(low, high)
            #new_value = (high+low)/2.0
            #print key, new_value
            #if key == 'T':
            #    print key, low, high, new_value
            setattr(pc, key, new_value)
        #pc.E = 8.0e9
        pc.L = L
        pc.d = d
        f0nat = numpy.sqrt(f0**2 + decays[0]**2)
        #print f0, f0nat
        pc, self.calc_f0, self.calc_B = match_actual(pc, f0nat, B, pc_ideal)
        #print "%.10f" % (B - calc_B)
        #pc = match_actual(pc, f0, B, pc_ideal)
        if pc is False:
            return False
        f_target = expected_frequencies.FREQS[self.inst_text][st_text]
        #print "tension correction for %.1f: old %.1f N\t" % (
        #    f_target, pc.T),
        pc.T = 4* f_target**2 * pc.pl * pc.L**2
        #print "new %.1f N" % (pc.T)

        # under-estimate
        pc.T *= 0.9

        ## estimate maximum frequency
        #n = 30
        #pi_div_l = math.pi / pc.L
        #I = math.pi * pc.d*pc.d*pc.d*pc.d / 64.0
        #n_pi_div_L = n*pi_div_l
        #div_pc_pl = 1.0 / pc.pl
        #w0n = math.sqrt( (pc.T * div_pc_pl) * n_pi_div_L*n_pi_div_L
        #          + ((pc.E * I * div_pc_pl)
        #          * n_pi_div_L*n_pi_div_L
        #          * n_pi_div_L*n_pi_div_L
        #          ))
        #if w0n > artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE * math.pi/2:
        #    return False


        #print "target:", f_target
        #for key in pc_ideal:
        #    print key, getattr(pc, key)
        #print "L", pc.L
        #exit(1)
        #pc.N = 17 # ensure no problems with aliasing
        #for i in range(SHORT_DECAYS):
        #    artifastring_instrument.floatArray_setitem(pc.modes, i, decays[i])


        pc.cutoff = CUTOFF_ORIG

        self.vln.set_physical_constants(st, pc)
        return True

    def pick_new_length(self):
        length_ideal = published_constants.PHYSICAL_CONSTANT_RANGES[self.inst_text]['L']
        low, high = length_ideal
        self.L_init = random.uniform(low, high)
        
    def pick_new_friction(self):
        friction_ideal = published_constants.FRICTION_CHARACTERISTICS[self.inst_text]
        friction = {}
        for key in friction_ideal:
            low, high = friction_ideal[key]
            new_value = random.uniform(low, high)
            #setattr(friction, key, new_value)
            friction[key] = new_value
        self.friction_init = friction

    def schelleng_max(self, st, beta, vb):
        pc = self.vln.get_physical_constants(st)
        Zc = numpy.sqrt(pc.T * pc.pl)
        us = self.friction['s']
        ud = self.friction['d']
        #v0 = self.friction['v0']
        force_max = 2* vb * Zc / (beta*(us-ud))
        #force_max = 2*Zc/(us-ud) * (vb + beta*v0) / beta
        #print force_max
        return force_max

    def new_constants(self, st, st_text, f0, B, L, d):
        stable = False

        while not stable:
            #self.vln.set_string_logfile(st, 'string.log')
            while True:
                ret = self.pick_new_constants(st, st_text,
                    f0, B, L, d)
                if ret:
                    break
            #Lrange = published_constants.PHYSICAL_CONSTANT_RANGES[self.inst_text]['L']
            #L = (Lrange[0] + Lrange[1]) / 2.0
            beta = 0.12
            vb = 0.3
            bow_force = self.schelleng_max(st, beta=beta, vb=vb)
            bow_force *= 0.2
            #print "bow force:", bow_force
            stable = self.test_stable(st, beta=beta,
                bow_force=bow_force, vb=vb)
            if stable:
                f_target = expected_frequencies.FREQS[self.inst_text][st_text]
                pc_ideal = published_constants.PHYSICAL_CONSTANT_RANGES[self.inst_text][st_text]
                T_bounds = pc_ideal['T']
                #self.vln.set_string_logfile(st, "")
                #print "before tuning", st, f_target, T_bounds
                if PAUSES:
                    raw_input()
                print self.vln.get_physical_constants(st).T
                stable = self.tune(st, f_target,
                    T_bounds[0]*0.8, T_bounds[1]*1.2,
                    beta=beta, bow_force=bow_force, vb=vb)
                print self.vln.get_physical_constants(st).T
                #print stable
            #self.add_arff(stable)

    def hop_pitch(self, wavfile=None):
        #buf = wavfile.request_fill(HOPSIZE)
        #stable = artifastring_instrument.wait_samples_c(self.vln, buf, HOPSIZE)
        stable = self.vln.wait_samples(self.audio_out_buf)
        if stable > 0:
            #print "bail stable 5"
            return False
        for i in xrange(HOPSIZE):
            aubio.aubiowrapper.fvec_write_sample(
                #self.fvec, float(buf[i]), 0, i)
                self.fvec, float(self.audio_out_buf[i]), 0, i)
        self.pitches[self.pi] = aubio.aubiowrapper.aubio_pitchdetection(
            self.pitch_obj, self.fvec)
        #print self.pitches[self.pi]
        self.pi = (self.pi + 1) % NUM_PITCH_AVERAGE
        return True

    def tune(self, st, f_target, T_low, T_high, beta, bow_force, vb):
        self.pitches = numpy.zeros(NUM_PITCH_AVERAGE)
        self.pi = 0

        bow_accel = 0.2
        K_p = 0.1
        INITIAL_SECONDS = 1.0
        self.vln.reset()
        self.vln.finger(st, 0, 1.0)
        #self.vln.bow(st, beta, bow_force, vb)
        self.vln.bow_accel(st, beta, bow_force, vb, bow_accel)
        #wavfile = monowav.MonoWav("pc-consts/test-pitch.wav")
        pitches_wav_array = numpy.array(0, dtype=numpy.int16)

        # start string vibrating
        for i in range(int(INITIAL_SECONDS *
                artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE
                / float(HOPSIZE))):
            stabletrue = self.hop_pitch()
            pitches_wav_array = numpy.append(
                pitches_wav_array, self.audio_out_buf)
            if not stabletrue:
                #print "bail stable 3"
                scipy.io.wavfile.write("pc-consts/test-pitches-%i.wav" % st,
                    artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE,
                    pitches_wav_array)
                return False
            #print "%.1f" % (pitch)
        while True:
            for i in xrange(NUM_PITCH_AVERAGE):
                stabletrue = self.hop_pitch()
                pitches_wav_array = numpy.append(
                    pitches_wav_array, self.audio_out_buf)
                if not stabletrue:
                    scipy.io.wavfile.write("pc-consts/test-pitches-%i.wav" % st,
                        artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE,
                        pitches_wav_array)
                    #print "bail stable 4"
                    return False
                pitch = numpy.median(self.pitches)
                #print self.pitches
                #print "%.1f" % (pitch)
            if pitch < 10:
                #print "unstable"
                return False
                #raise Exception("Invalid pitch")
            delta_pitch = f_target - pitch
            if abs(delta_pitch) / f_target < 1e-3:
                #print "%.1f\t%.1f" % (
                #    pitch, delta_pitch)
                break
            pc = self.vln.get_physical_constants(st)
            #alt_mul = 1.0 + K_p * delta_pitch
            pc.T += K_p * delta_pitch
            #print self.pitches
            #print "%.1f\t%.1f\t%.3f\t%.1f" % (
            #    pitch, delta_pitch, 0, pc.T)
            scipy.io.wavfile.write("pc-consts/test-pitches-%i.wav" % st,
                artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE,
                pitches_wav_array)
            if pc.T < T_low or pc.T > T_high:
                #print "bail; bad tension: %.2f N" % pc.T
                #print "inst %s string %i inst_num %s" % (
                #    self.inst_text, st, self.inst_num_text)
                #print "should be between %.2f and %.2f" % (T_low, T_high)
                #exit(1)
                return False
            self.vln.set_physical_constants(st, pc)
        #exit(1)
        for i in range(4):
            stabletrue = self.hop_pitch()
            pitches_wav_array = numpy.append(
                pitches_wav_array, self.audio_out_buf)
        scipy.io.wavfile.write("pc-consts/test-pitches-%i.wav" % st,
            artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE,
            pitches_wav_array)
        print "written to test-pitches-%i.wav" % st
        pc = self.vln.get_physical_constants(st)
        #try:
        #    print "final tuning:\t%.1f N" % pc.T
        #except:
        #    print "tuning already perfect"
        if pc.T < T_low or pc.T > T_high:
            print "bail; bad tension: %.2f N" % pc.T
            print "should be between %.2f and %.2f" % (T_low, T_high)
            return False
        print pitch
        return True

    @staticmethod
    def spectral_flatness(memory_buf):
        buf = numpy.empty(HOPSIZE)
        for i in xrange(HOPSIZE):
            buf[i] = memory_buf[i]
        if all(buf == 0):
            return False
        fft = scipy.fftpack.fft(buf)
        fft_power = abs(fft[:len(fft)/2])**2
        flatness = (scipy.stats.gmean(fft_power) / fft_power.mean() )
        #pylab.semilogy(fft_power)
        #pylab.show()
        return flatness

    @staticmethod
    def spectral_forces(memory_buf):
        buf = numpy.empty(HOPSIZE/4)
        for i in xrange(HOPSIZE/4):
            buf[i] = memory_buf[i]
        fft = scipy.fftpack.fft(buf)
        fft_power = abs(fft[:len(fft)/2])**2
        freqs = numpy.array([ i*11025/(HOPSIZE/4)
            for i in range(len(fft_power))] )
        #pylab.figure()
        #pylab.plot(buf)
        pylab.figure()
        pylab.semilogy(freqs, fft_power)
        pylab.show()
        return True


    def test_stable(self, st, beta, bow_force, vb):
        self.vln.reset()
        wavfile = monowav.MonoWav("pc-consts/test-stable.wav")
        for i in range(int(TEST_SECONDS * artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE / HOPSIZE)):
            self.vln.finger(st, 0.251, 1.0)
            self.vln.bow(st, beta, bow_force, vb)
            buf = wavfile.request_fill(HOPSIZE)
            #stable = self.vln.wait_samples(self.audio_out_buf)
            stable = artifastring_instrument.wait_samples_c(self.vln, buf, HOPSIZE)
            #print stable
            if stable > 0:
                print stable
                print "bail stable 1"
                print bow_force
                #exit(1)
                return False
            #self.vln.wait_samples_forces(self.audio_out_buf,
            #    self.force_out_buf, HOPSIZE)
            #if not stable:
            #    return False
        #print 'ok'
        #exit(1)
        stable = self.vln.wait_samples(self.audio_out_buf)
        #print stable
        if stable > 0:
            print "bail stable 2"
            return False
        #self.vln.wait_samples_forces(self.audio_out_buf,
        #   self.force_out_buf, HOPSIZE)
        #if not stable:
         #   return False
        #flatness = self.spectral_flatness(self.audio_out_buf)
        #force_ok = self.spectral_forces(self.force_out_buf)
        #if not flatness:
        #    print "bail flatness 1"
        #    return False
        #print flatness
        #if flatness > MAX_SPECTRAL_FLATNESS:
        #    print "bail flatness 2"
        #    return False
        return True

    def test_pluck(self, seconds=1.0):
        num_samples = int(seconds*artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE)
        print "not implemented"
        #buf = self.wavfile.request_fill(num_samples)
        #self.vln.pluck(self.st, 0.48, 1.0)
        #self.vln.wait_samples(buf, num_samples)

    def test_bow(self, basename, st, seconds=1.0):
        self.vln.reset()
        self.wavfile = monowav.MonoWav(basename + ".wav")
        num_samples = int(seconds*artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE)
        #self.vln.bow(self.st, 0.12, 0.33, 0.25)
        self.vln.bow(st, 0.12, 0.1, 0.2)
        for i in range(int(num_samples / HOPSIZE)):
            buf = self.wavfile.request_fill(HOPSIZE)
            self.vln.wait_samples(buf, HOPSIZE)

    #def add_arff(self, stable):
    #    pc_arff = self.vln.get_physical_constants(self.st)
    #    pc_ideal = published_constants.PHYSICAL_CONSTANT_RANGES[self.inst_text][self.st_text]
    #    for key in pc_ideal:
    #        low, high = pc_ideal[key]
    #        normalized_value = (getattr(pc_arff, key) - low) / (high-low)
    #        setattr(pc_arff, key, normalized_value)
    #    friction_ideal = published_constants.FRICTION_CHARACTERISTICS[self.inst_text][self.st_text]
    #    friction_normalized = dict(self.friction)
    #    for key in friction_ideal:
    #        low, high = friction_ideal[key]
    #        new_value = (self.friction[key] - low) / (high-low)
    #        #setattr(friction, key, new_value)
    #        friction_normalized[key] = new_value
    #    self.attempts.append( [
    #        pc_arff.T, pc_arff.L, pc_arff.d, pc_arff.pl, pc_arff.E,
    #        friction_normalized['s'], friction_normalized['d'], friction_normalized['v0'],
    #        stable] )

def predicted_f0_B_two(pc, xs):
    pl = xs[0]
    T = xs[1]
    L = xs[3]

    B = 0.
    f0 = numpy.sqrt( T / pl * (numpy.pi / L)**2) / (2*numpy.pi)
    return numpy.array([f0, B])

def predicted_f0_B(pc, xs):
    if any(xs < 0):
        return numpy.array([1e9, 1e9])
    pl = xs[0]
    T = xs[1]
    E = xs[2]
    L = xs[3]
    d = xs[4]

    B = (E * numpy.pi**3 * d**4) / (64.0 * L**2 * T)
    I = numpy.pi * (d**4) / 64.0
    #f0 = numpy.sqrt( T / pl * (numpy.pi / L)**2) / (2*numpy.pi)
    f0 = numpy.sqrt( T / pl * (numpy.pi / L)**2
        + E * I / pl * (numpy.pi / L)**4 ) / (2*numpy.pi)
    return numpy.array([f0, B])


def eval_pcs_two(xs, ys, pc):
    if any(xs < 0):
        return numpy.array([1e9, 1e9])
    #pred = predicted_f0_B_two(pc, xs)
    pred = predicted_f0_B(pc, xs)
    results = numpy.array([
        abs(ys[0] - pred[0])/ys[0], abs(ys[1] - pred[1])/ys[1],
        #abs(ys[0] - pred[0])/ys[0], 0.,
        (ys[2] - xs[0])/ys[2], (xs[0] - ys[3])/ys[3],
        (ys[4] - xs[1])/ys[4], (xs[1] - ys[5])/ys[5],
        (ys[6] - xs[2])/ys[6], (xs[2] - ys[7])/ys[7],
        (ys[8] - xs[3])/ys[8], (xs[3] - ys[9])/ys[9],
        (ys[10] - xs[4])/ys[10], (xs[4] - ys[11])/ys[11],
        ])
    for i in xrange(0,2):
        if results[i] < 1e-4:
            results[i] = 0
    for i in xrange(0, len(results)):
        if results[i] < 0:
            results[i] = 0
    weights = numpy.array([
        10, 1,
        1, 1, # pl
        1, 1, # T
        1, 1, # E
        10, 10, # L
        1, 1, # d
        ])
    results *= weights
    return results


def eval_pcs_all(xs, ys, pc):
    pred = predicted_f0_B(pc, xs)
    results = numpy.array([
        abs(ys[0] - pred[0])/ys[0], abs(ys[1] - pred[1])/ys[1],
        (ys[2] - xs[0])/ys[2], (xs[0] - ys[3])/ys[3],
        (ys[4] - xs[1])/ys[4], (xs[1] - ys[5])/ys[5],
        (ys[6] - xs[2])/ys[6], (xs[2] - ys[7])/ys[7],
        (ys[8] - xs[3])/ys[8], (xs[3] - ys[9])/ys[9],
        (ys[10] - xs[4])/ys[10], (xs[4] - ys[11])/ys[11],
        ])
    for i in xrange(0,2):
        if results[i] < 1e-4:
            results[i] = 0
    for i in xrange(0, len(results)):
        if results[i] < 0:
            results[i] = 0
    #print results
    weights = numpy.array([
        10, 10,
        1, 1, # pl
        1, 1, # T
        1, 1, # E
        10, 10, # L
        10, 10, # d
        ])
    results *= weights
    return results

def check_bounds(xs, pc_ideal):
    pl = xs[0]
    T = xs[1]
    E = xs[2]
    L = xs[3]
    d = xs[4]

    bad = 0
    def line(txt, var):
        if not (pc_ideal[txt][0] <= var <= pc_ideal[txt][1]):
            #print '-------- exceeds bounds:'
            #print "%s\t%.2e\t%.2e\t%.2e" % (txt,
            #    pc_ideal[txt][0], var, pc_ideal[txt][1])
            return 1
        #print "%s\t%.2e\t%.2e\t%.2e" % (txt,
        #   pc_ideal[txt][0], var, pc_ideal[txt][1])
        return 0
    bad += line('pl', pl)
    bad += line('T', T)
    bad += line('E', E)
    bad += line('L', L)
    bad += line('d', d)
    return bad
    
def match_actual(pc, f0nat, B, pc_ideal):
    initial_guess = numpy.array([pc.pl, pc.T, pc.E,
        pc.L, pc.d])
    ys = numpy.array([f0nat, B,
        pc_ideal['pl'][0], pc_ideal['pl'][1],
        pc_ideal['T'][0], pc_ideal['T'][1],
        pc_ideal['E'][0], pc_ideal['E'][1],
        pc_ideal['L'][0], pc_ideal['L'][1],
        pc_ideal['d'][0], pc_ideal['d'][1],
        ])

    fit, cov, infodict, mesg, ier = scipy.optimize.leastsq(
        eval_pcs_two, initial_guess,
        args=(ys, pc), full_output = 1)
    if 1 < ier > 4:
        print "problem"
    pred = predicted_f0_B(pc, fit)
    bad = check_bounds(fit, pc_ideal)
    if bad > 0:
        #print "%.1f\t%.1f\t\t%.3g\t%.3g" % (f0nat, pred[0], B, pred[1])
        #exit(1)
        return False, False, False
    #print "%.1f\t%.3g" % ( (f0nat - pred[0])/f0nat, (B - pred[1])/B)

    #initial_guess = numpy.array([
    #    fit[0], fit[1], pc.E, fit[2], pc.d,
    #    ])
    initial_guess = fit
    fit, cov, infodict, mesg, ier = scipy.optimize.leastsq(
        #eval_pcs_two, initial_guess,
        eval_pcs_all, initial_guess,
        args=(ys, pc), full_output = 1)
    if 1 < ier > 4:
        print "problem"
    pred = predicted_f0_B(pc, fit)
    #print "%.1f\t%.3g" % ( (f0nat - pred[0])/f0nat, (B - pred[1])/B)

    #res = eval_pcs_all(fit, ys, pc)
    bad = check_bounds(fit, pc_ideal)
    if bad > 0:
        #print "bail with:"
        #print "%.1f\t%.1f\t\t%.3g\t%.3g" % (f0nat, pred[0], B, pred[1])
        #global global_count
        #global_count += 1
        #if global_count > 4:
        #    exit(1)
        #exit(1)
        return False, False, False
    pc.pl = fit[0]
    pc.T = fit[1]
    pc.E = fit[2]
    pc.L = fit[3]
    pc.d = fit[4]

    return pc, pred[0], pred[1]


def file_line_num(inst_num, inst_within_num, st_num):
    if inst_num == 0:
        num = 0
        num += inst_within_num
        num += (3-st_num)*5
    elif inst_num == 1:
        num = 20
        num += inst_within_num
        num += (3-st_num)*2
    elif inst_num == 2:
        num = 28
        num += inst_within_num
        num += (3-st_num)*3
    return num

def get_length_diameter(inst_num, inst_within_num, st_num):
    lines = open("../distances/dists.txt").readlines()
    #print inst_num, inst_within_num, st_num
    num = file_line_num(inst_num, inst_within_num, st_num)
    i = 0
    for l in lines:
        if len(l) < 2:
            continue
        if l[0] == 'n':
            continue
        if l[0] == '#':
            continue
        if i == num:
            L = float(l.split()[1])
            d = float(l.split()[2]) * 0.001
            return L, d
        i += 1
    return 0, 0

def get_f0_B(inst_num, inst_within_num, st_num):
    lines = open("../mode-detect/out/string-Bs.txt").readlines()
    #print inst_num, inst_within_num, st_num
    num = file_line_num(inst_num, inst_within_num, st_num)
    i = 0
    for l in lines:
        if len(l) < 2:
            continue
        if l[0] == 'n':
            continue
        if l[0] == '#':
            continue
        if i == num:
            f0 = float(l.split('&')[1])
            B = float(l.split('&')[2])
            return f0, B
        i += 1
    return 0, 0


def do_inst_num(inst_num, inst_text, inst_within_num, inst_num_text, st_texts):
    inst = Inst(inst_num, inst_text, inst_num_text)
#inst = Inst(0, 'violin', 2, 'a')

    inst_const_text = ""
    inst_const_text += "    {   // %s %s %s\n" % (
        inst_num, inst_text, inst_num_text)
    inst_const_text += "       " # yes only 7 spaces here
    rows = []
    for st, st_text in enumerate(st_texts):
        #if inst_within_num < 2:
        #    continue
        print "doing inst within st nums:", inst_num, inst_within_num, inst_text, st, st_text
        L, d = get_length_diameter(inst_num, inst_within_num, st)
        f0, B = get_f0_B(inst_num, inst_within_num, st)
        inst.new_constants(st, st_text, f0, B, L, d)
        cutoff_value = cutoff.do_string(inst.vln, inst_num, st)
        pc = inst.vln.get_physical_constants(st)
        pc.cutoff = cutoff_value
        inst.vln.set_physical_constants(st, pc)
        st_const_text, row = inst.get_constants_text(st, st_text)
        rows.append(row)
        inst_const_text += st_const_text
    inst_const_text += "\n    },\n"
    return inst_const_text, rows


def do_inst_type(inst_num, inst_text):
    num_texts = available_instruments.INSTRUMENTS[inst_text][0]
    st_texts = available_instruments.INSTRUMENTS[inst_text][1]
    text = ""
    upper = inst_text.upper()
    text += "/* This file was generated automatically by make-constants.py\n"
    text += " * *** DO NOT EDIT ***\n"
    text += " */\n"
    text += "#ifndef %s_CONST\n" % upper
    text += "#define %s_CONST\n" % upper
    #text += "#include \"config.h\"\n"
    text += "\n"
    text += "const int CONSTANTS_%s_NUM = %i;\n" % (upper, len(num_texts))
    text += "const String_Physical %s_params[%i][%i] =\n" % (
        inst_text, len(num_texts), len(st_texts))
    text += "{   // %s %s\n" % (inst_num, inst_text)
    rowss = []
    for inst_within_num, vnt in enumerate(num_texts):
        vnt_text, rows = do_inst_num(inst_num, inst_text,
            inst_within_num, vnt, st_texts)
        text += vnt_text
        rowss.extend(rows)
    text += "};\n"
    text += "#endif\n"

    out = open(os.path.join("pc-consts",
        "strings_%s.h" % inst_text ), 'w')
    out.write(text)
    out.close()

    return rowss

def get_split_filename(dirname):
    return os.path.basename(dirname).split('-')

def sort_inst_names(a):
    at = get_split_filename(a.split('&')[0])
    value = 0
    ### instrument type
    if at[0] == 'violin':
        value += 100
    elif at[0] == 'viola':
        value += 200
    elif at[0] == 'cello':
        value += 300
    else:
        print "Don't recognize that instrument:", at[0]
    ### string
    if at[1] == 'e':
        value += 10
    elif at[1] == 'a':
        value += 20
    elif at[1] == 'd':
        value += 30
    elif at[1] == 'g':
        value += 40
    elif at[1] == 'c':
        value += 50
    else:
        print "Don't recognize string:", at[1]
    ### instrument owner
    if at[2] == 'glasgow':
        value += 1
    elif at[2] == 'colin':
        value += 2
    elif at[2] == 'graham':
        value += 3
    elif at[2] == 'jen':
        value += 4
    elif at[2] == 'mom':
        value += 5
    elif at[2] == 'wilf':
        value += 6
    elif at[2] == 'wcams':
        value += 8
    elif at[2] == 'old':
        value += 9
    elif at[2] == 'I':
        value += 1
    elif at[2] == 'II':
        value += 2
    elif at[2] == 'III':
        value += 3
    elif at[2] == 'IV':
        value += 4
    elif at[2] == 'V':
        value += 5
    else:
        print "Don't recognize owner:", at[2]
    return value

def main():
    rowsss = []
    for itn, inst_text in enumerate(['violin', 'viola', 'cello']):
        rowss = do_inst_type(itn, inst_text)
        rowsss.extend(rowss)

    rowsss = sorted(rowsss, key=sort_inst_names)

    out = open(os.path.join("pc-consts", "strings-constants.txt"), 'w')
    out.write("name&T&L&d&pl&E&mus&mud&v0&cutoff\n")
    out.write('\n'.join( rowsss ))
    out.close()

#inst = Inst(0, 'violin', 'I')
#inst.new_constants(3, 'e')
#st_const_text, row = inst.get_constants_text(3, 'e')
#print row
main()

#data = inst.attempts

#arff.dump('result.arff', data, relation='whatever',
#    names=[
#        'T', 'L', 'd', 'pl', 'E',
#        's', 'd', 'v0',
#        'stable'])

