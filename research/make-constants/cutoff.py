#!/usr/bin/env python

CUTOFF_DB_FINAL_AUDIO = 10

#STRINGS = [
#  (0,0), (0,1), (0,2), (0,3), (0,4),
#  (1,0), (1,1),
#  (2,0), (2,1), (2,2), (2,3)
#  ]
INST_FORCES = [
  [1.5,1.0,1.0,0.5],
  [1.75,1.0,1.0,0.5],
  [2.0,0.9,0.8,0.6],
  ]


import sys
sys.path.append('../../build/swig')
sys.path.append('../../build/.libs')
sys.path.append('../shared')


import math
import numpy
import dsp

import artifastring_instrument
#import monowav
import midi_pos

import scipy
import pylab

HOPSIZE = artifastring_instrument.NORMAL_BUFFER_SIZE
FORCE_SIZE = HOPSIZE / artifastring_instrument.HAPTIC_DOWNSAMPLE_FACTOR

def pluck_force(violin, st, force, finger, plot=False, write=False):
    #violin = artifastring_instrument.ArtifastringInstrument(inst, instnum)
    #wavfile = monowav.MonoWav("artifastring-test.wav")

    violin.reset()
    violin.finger(st, finger)
    violin.pluck(st, 0.2, force)
    
    def hop():
        buf = numpy.empty(HOPSIZE, dtype=numpy.int16)
        forces = numpy.empty(FORCE_SIZE, dtype=numpy.int16)
        violin.wait_samples_forces_python(buf, forces)
        string_array = numpy.zeros(4*HOPSIZE, dtype=numpy.float32)
        string_array_size = violin.get_string_buffer(st, string_array)
        string_array = string_array[:string_array_size]
        #pylab.plot(string_array)
        #pylab.show()

        buf_rms = numpy.sqrt(numpy.mean(numpy.array(buf,
            numpy.float64)**2))
        sa_rms = numpy.sqrt(numpy.mean(numpy.array(string_array,
            dtype=numpy.float64)**2))
        buf_ss = numpy.sum(numpy.array(buf,
            numpy.float64)**2)
        sa_ss = numpy.sum(numpy.array(string_array,
            dtype=numpy.float64)**2)
        return buf_rms, sa_rms, buf_ss, sa_ss
    
    dh = float(HOPSIZE) / artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE
    BUFS = 1000
    dhs = numpy.arange(0, BUFS) * dh
    
    buf = numpy.zeros(BUFS)
    sa = numpy.zeros(BUFS)
    buf_sss = numpy.zeros(BUFS)
    sa_sss = numpy.zeros(BUFS)
    for i in range(BUFS):
        buf_this, string_array_this, buf_ss, sa_ss = hop()
        buf[i] = buf_this
        sa[i] = string_array_this
        buf_sss[i] = buf_ss
        sa_sss[i] = sa_ss
    
    buf_db = dsp.amplitude2db(buf)
    sa_db = dsp.amplitude2db(sa)
    
    cutoff_hop = 0
    for i in range(BUFS):
        if buf_db[i] < CUTOFF_DB_FINAL_AUDIO:
            cutoff_hop = i
            break
    print "cutoff time:", cutoff_hop*dh
    
    cutoff_internal_audio = sa_sss[cutoff_hop]
    cutoff_internal_audio_db = sa_db[cutoff_hop]
    #print "Cutoff internal audio:", cutoff_internal_audio
    if write:
        numpy.savetxt("instrument-%i-%.3f-db.txt" % (
                st,finger),
            numpy.vstack( (
                dhs, buf_db
                )).transpose())
        numpy.savetxt("string-%i-%.3f-db.txt" % (
                st,finger),
            numpy.vstack( (
                dhs, sa_db
                )).transpose())
        numpy.savetxt("cutoff-%i-%.3f.txt" % (
                st,finger),
                numpy.array([
                    [0,
                    cutoff_internal_audio_db],
                    [BUFS*dh,
                    cutoff_internal_audio_db]
                    ])
                )

    if plot:
        pylab.subplot(211)
        pylab.title("Final audio")
        pylab.plot(dhs, buf_db)
        pylab.axhline(CUTOFF_DB_FINAL_AUDIO)
    
        pylab.subplot(212)
        pylab.title("String audio")
        pylab.plot(dhs, sa_db, '.-')
        pylab.axhline(cutoff_internal_audio_db)
        pylab.show()
    return cutoff_internal_audio

def do_string(violin, insttype, st, plot=False, write=False):
    force = INST_FORCES[insttype][st]

    MIDI = numpy.arange(0, 13)
    POS = [ midi_pos.midi2pos(float(m)) for m in MIDI]
    vals = []
    #dbs = []
    for finger in POS:
        val = pluck_force(violin=violin,
            st=st, force=force, finger=finger,
            plot=plot, write=write,
            )
        vals.append(val)
        #dbs.append(db)
    val = min(vals)
    #db = max(dbs)
    return val


#for inst, instnum in STRINGS:
#    forces = INST_FORCES[inst]
#    for st, force in enumerate(forces):
#            val, db = do_string(inst=inst, instnum=instnum,
#                st=st, force=force,
#                #plot=True
#            )
#            print inst, instnum, st, val


if __name__ == "__main__":
    violin = artifastring_instrument.ArtifastringInstrument(0, 0)
    do_string(violin, 0, 3, plot=False, write=True)


