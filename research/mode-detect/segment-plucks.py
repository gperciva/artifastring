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

onset_threshold = int(median + 7*stddev)
wait = int(6.0 * sample_rate)
look_maximum = int(2.0 * sample_rate)
omit_last_samples = int(3.0 * sample_rate)
initial_silence = int(10.0 * sample_rate)
max_samples = int(10.0 * sample_rate)


print "Processing",
sys.stdout.flush()

#exit(1)
boundaries = []
last_sample = -wait


i = 0
for sample in data_abs:
    #print sample, onset_threshold
    if sample > onset_threshold:
        if i > (last_sample + wait):
            print ".",
            sys.stdout.flush()
            # find maximum
            cands = data[i:i+look_maximum]
            add_sample_index = cands.argmax()
            cands = data[add_sample_index:]
            # find next zero-crossing
            if cands[0] < 0:
                direction = 1
            else:
                direction = -1
            for j, val in enumerate(cands):
                if val*direction > 0:
                    last_sample = i + j + add_sample_index
                    break
            boundaries.append(last_sample)
    i += 1
boundaries.append(len(data))
print

splitted_files = 1
filename = ""
for start, end in zip(boundaries[:-1], boundaries[1:]):
    end -= omit_last_samples
    this_data = data[start:end]
    this_data = this_data[:max_samples]
    filename = os.path.join(split_dir,
            os.path.basename( orig_filename.replace(".wav",
                "-%02i.wav" % splitted_files)))
    scipy.io.wavfile.write(filename, sample_rate, this_data)
    splitted_files += 1

print "Found: %i plucks, from %s" % (len(boundaries)-1, orig_filename)


noise_dir = split_dir.replace("fixed-wav", "noise")
noise = data[0:initial_silence]
filename = os.path.join(noise_dir,
    os.path.basename( orig_filename.replace(".wav",
        "-noise.wav")))
scipy.io.wavfile.write(filename, sample_rate, noise)


