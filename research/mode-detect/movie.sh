#!/bin/sh
BASENAME=$1
FPS=5
DIR="mf://spectrum/${BASENAME}/*.png"
mencoder ${DIR} -mf type=png:fps=${FPS} -ovc \
   lavc -lavcopts vcodec=wmv2 -oac copy -o spectrum/${BASENAME}.avi


