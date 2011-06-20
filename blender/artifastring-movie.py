#!/usr/bin/env python

import optparse
import subprocess
import sys
import os
import glob

def get_options():
    parser = optparse.OptionParser(
        description="Combines a .wav and *.tga into a movie for Artifastring.")
    parser.add_option("-o", "--output",
        default=None,
        help="Output filename")
    parser.add_option("-i", "--images-dir",
        default="/tmp/artifastring-images/",
        help="Directory of images")
    parser.add_option("-l", "--logfile",
        default="render.log",
        help="Log filename (relative to output dir)")
    parser.add_option("--fps",
        metavar="N", default="25",
        help="Frames per second")
    parser.add_option("--h264",
        action="store_true",
        help="Generate avi with h264 instead of mpeg-2")
    (options, args) = parser.parse_args()
    try:
        options.audio_filename = args[0]
    except IndexError:
        print "Error: must have an audio filename"
        parser.print_help()
        return None
    return options.__dict__

MPEG = """mencoder \
    "mf://%(images_dir)s/*.tga" \
    -mf fps=%(fps)s:type=tga \
    \
-ovc lavc \
-lavcopts \
vcodec=mpeg1video:vbitrate=1152:keyint=15:mbd=2 \
\
-oac mp3lame \
-audiofile %(audio_filename)s \
-o %(output)s
"""

H264 = """mencoder \
    "mf://%(images_dir)s/*.tga" \
    -mf fps=%(fps)s:type=tga \
    \
-ovc lavc \
-lavcopts \
vcodec=mpeg4:mbd=1:vbitrate=2000 \
\
-oac mp3lame \
-audiofile %(audio_filename)s \
-o %(output)s
"""

def main():
    options = get_options()
    if not options:
        exit()

    if options['h264']:
        if not options['output']:
            options['output'] = "artifastring-movie.avi"
        cmd = H264 % options
    else:
        if not options['output']:
            options['output'] = "artifastring-movie.mpeg"
        cmd = MPEG % options

    log_filename = options['logfile']
    logfile = open(log_filename, 'w')
    #print cmd
    p = subprocess.Popen(cmd, shell=True, stdout=logfile)
    p.wait()
    logfile.close()

main()

