#!/bin/sh
SPLIT_PNG=split-png/
mkdir -p $SPLIT_PNG

#rm -f *.pickle
./pluck-detect.py violin-e
./pluck-detect.py violin-a
./pluck-detect.py violin-d
./pluck-detect.py violin-g

./pluck-detect.py cello-a
./pluck-detect.py cello-d
./pluck-detect.py cello-g
./pluck-detect.py cello-c

mv violin_?_modes.h ../artifastring/
mv cello_?_modes.h ../artifastring/

