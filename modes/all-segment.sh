#!/bin/sh
ORIGINAL_DIR=original_recordings/
DEST_DIR=split-wav/
mkdir -p $DEST_DIR

./segment-plucks.py $ORIGINAL_DIR/violin-e.wav $DEST_DIR/
./segment-plucks.py $ORIGINAL_DIR/violin-a.wav $DEST_DIR/
./segment-plucks.py $ORIGINAL_DIR/violin-d.wav $DEST_DIR/
./segment-plucks.py $ORIGINAL_DIR/violin-g.wav $DEST_DIR/

./segment-plucks.py $ORIGINAL_DIR/cello-a.wav $DEST_DIR/
./segment-plucks.py $ORIGINAL_DIR/cello-d.wav $DEST_DIR/
./segment-plucks.py $ORIGINAL_DIR/cello-g.wav $DEST_DIR/
./segment-plucks.py $ORIGINAL_DIR/cello-c.wav $DEST_DIR/

