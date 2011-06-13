#!/bin/sh
SAMPLES=512


OUT=violin_body_impulse.h
echo "// This file was automatically generated" > $OUT
echo "#ifndef IMPULSE_DATA_H" >> $OUT
echo "#define IMPULSE_DATA" >> $OUT
echo "const int PC_KERNEL_SIZE = $SAMPLES;" >> $OUT
echo "const double pc_kernel[] = {" >> $OUT
sox impulse-$SAMPLES.wav -t dat - | \
        awk '$1 != ";" { print "   ", $2, ","}' >> $OUT
echo "};" >> $OUT
echo "#endif" >> $OUT

