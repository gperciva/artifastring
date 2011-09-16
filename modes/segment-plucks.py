#!/usr/bin/env python

import sys
import os.path

import scipy.io.wavfile
import numpy

try:
    orig_filename = sys.argv[1]
    split_dir = sys.argv[2]
except:
    print "Need wave filename to split, and directory to put them"
    sys.exit(1)


sample_rate, data = scipy.io.wavfile.read(orig_filename)
#data = data_unnormalized / float(numpy.iinfo(data_unnormalized.dtype).max)
data_abs = abs(data)


median = numpy.median(data_abs)
stddev = numpy.std(data_abs)
onset_threshold = int(median + 5*stddev)
wait = int(5.0 * 44100)


print "Processing",
sys.stdout.flush()
boundaries = []
last_sample = -wait
for i, sample in enumerate(data_abs):
    #print sample, onset_threshold
    if sample > onset_threshold:
        if i > (last_sample + wait):
            print ".",
            sys.stdout.flush()
            last_sample = i
            boundaries.append(i)
boundaries.append(len(data))
print


splitted_files = 1
filename = ""
for start, end in zip(boundaries[:-1], boundaries[1:]):
    this_data = data[start:end]
    filename = os.path.join(split_dir,
            os.path.basename( orig_filename.replace(".wav",
                "-%02i.wav" % splitted_files)))
    scipy.io.wavfile.write(filename, sample_rate, this_data)
    splitted_files += 1

print "Found: %i plucks, from %s" % (len(boundaries)-1, orig_filename)

