#!/usr/bin/env python

import optparse
import subprocess
import sys
import os
import glob

def check_blender_version(min_version):
    cmd = "blender --version"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    p.wait()
    version = float(p.communicate()[0].split()[1])
    if version < min_version:
        print "Sorry, you need at Blender version >= 2.57"
        return False
    return True

def get_options():
    parser = optparse.OptionParser(
    	description="Generates images from an .actions files")
    parser.add_option("-o", "--output-dir",
    	default="/tmp/artifastring/images/",
    	help="Directory for output images")
    parser.add_option("--fps",
    	metavar="N", default="25",
    	help="Frames per second")
    parser.add_option("-s", "--start",
    	metavar="N", default="1",
    	help="Start frame")
    parser.add_option("-e", "--end",
    	metavar="N", default="0",
    	help="End frame (0 means end of file)")
    parser.add_option("-q", "--quality",
    	metavar="N", default="0",
    	help="Quality of rending: 0 (terrible) to 2 (best)")
    (options, args) = parser.parse_args()
    try:
        options.audio_filename = args[0]
    except IndexError:
        print parser.print_help()
        return None
    if not options.filename:
        print "Must have a filename"
        return None
    return options.__dict__

def prepare_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    oldfiles = glob.glob(os.path.join(dirname, '*.tga'))
    for filename in oldfiles:
        os.remove(filename)
    logfile = os.path.join(dirname, 'render.log')
    if os.path.exists(logfile):
        os.remove(logfile)
    return True

BLENDER_COMMAND = """blender -noaudio \
  -b %(blender_model)s \
  -P ${datarootdir}/artifastring/artifastring-blender.py \
  -o %(output_dir)s/#### \
  -s %(start)s %(end_flag)s -a \
  -- \
  -f %(filename)s \
  --fps %(fps)s \
  -q %(quality)s \
  > %(output_dir)s/render.log
  """

def generate_images(options):
    # workaround for behavior of blender -e option
    if options['end'] == '0':
        options['end_flag'] = ""
    else:
        options['end_flag'] = "-e %(end)s" % options
    if options['quality'] == '0':
        options['blender_model'] = "${datarootdir}/artifastring/fast-violin.blend"
    else:
        options['blender_model'] = "${datarootdir}/artifastring/violin-and-bow.blend"
    cmd = BLENDER_COMMAND % options
    #print cmd
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    p.wait()

if check_blender_version(2.56):
    options = get_options()
    if options:
        if prepare_dir(options['output_dir']):
            if os.path.exists(options['filename']):
                generate_images(options)
            else:
                print "ERROR: filename does not exist!"


