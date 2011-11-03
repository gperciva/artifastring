#!/usr/bin/env python

import numpy
import pylab

from defs_measure import FORMAT_NUMPY

SIZE = 2**16
#SIZE = 2**24

class SineInt():
    def __init__(self, freq=1.0, sample_rate=44100):
        if FORMAT_NUMPY == numpy.int16:
            multiplier = SIZE/2 - 1
        else:
            multiplier = 1.0
        self.lookup = FORMAT_NUMPY(
            multiplier * numpy.sin(numpy.linspace(0,
                2*numpy.pi, SIZE)))
        #print self.lookup.dtype
        self.index = 0.
        self.index_advance = 0.
        self.sample_rate = sample_rate

        self.set_freq(float(freq))
        #pylab.plot(self.lookup)
        #pylab.show()

    def set_freq(self, freq):
        self.index_advance = freq * SIZE / self.sample_rate

    def fill_buffer(self, buf):
        # TODO: speed this up
        for i in range(len(buf)):
            #buf[i] = self.lookup[int(self.index)]
            buf[i] = self.lookup[self.index]
            self.index += self.index_advance
            if self.index >= SIZE:
                self.index -= SIZE

def test():
    a = SineInt(440.0, 44100)
    #buf = numpy.zeros(8)
    buf = numpy.zeros( 44100, dtype=FORMAT_NUMPY )
    #print buf.dtype
    a.fill_buffer(buf)
    pylab.plot(buf)
    pylab.show()

if __name__ == "__main__":
    test()


