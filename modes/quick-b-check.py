#!/usr/bin/env python

import os
import os.path
import sys
import glob

dirs = glob.glob("spectrum/*")
dirs.sort()
for f in dirs:
    last = f.split("/")[1]
    cmd = "python plot-harmonics.py %s" % last
    print cmd
    os.system(cmd)

    cmd = "sh movie.sh %s" % last
    print cmd
    os.system(cmd)

#os.system("mv spectrum/*/*.png spectrum")

