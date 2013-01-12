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
    parser.add_option("-l", "--logfile",
        default="render.log",
        help="Log filename (relative to output dir)")
    parser.add_option("--fps",
        metavar="N", default="25",
        help="Frames per second")
    parser.add_option("--cycle-cameras",
        metavar="X", default="0",
        help="Change cameras every X seconds")
    parser.add_option("-s", "--start",
        metavar="N", default="1",
        help="Start frame")
    parser.add_option("-e", "--end",
        metavar="N", default="0",
        help="End frame (0 means end of file)")
    parser.add_option("-q", "--quality",
        metavar="N", default="0",
        help="Quality of rending: 0 (terrible) to 2 (best)")
    parser.add_option("-c", "--clean",
        action="store_true",
        help="Remove previous *.tga and *.log files from output directory")
    (options, args) = parser.parse_args()
    try:
        options.actions_filename = args[0]
    except IndexError:
        print parser.print_help()
        return None
    return options.__dict__

def prepare_dir(options):
    dirname = options['output_dir']
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if options['clean']:
        map(os.remove,
            glob.glob(os.path.join(dirname, '*.tga')) +
            glob.glob(os.path.join(dirname, '*.log')))
    return True

BLENDER_COMMAND = """blender -noaudio \
  -b %(blender_model)s \
  -P ${datarootdir}/artifastring/artifastring_blender.py \
  -o %(output_dir)s/#### \
  -s %(start)s %(end_flag)s -a \
  -- \
  -f %(actions_filename)s \
  --fps %(fps)s \
  --cycle-cameras %(cycle_cameras)s \
  -q %(quality)s \
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
    log_filename = os.path.join(options['output_dir'], options['logfile'])
    logfile = open(log_filename, 'w')
    #print cmd
    p = subprocess.Popen(cmd, shell=True, stdout=logfile)
    p.wait()
    logfile.close()

# process options first, so that we can view --help without blender
options = get_options()
if check_blender_version(2.56):
    if options:
        if prepare_dir(options):
            if os.path.exists(options['actions_filename']):
                generate_images(options)
            else:
                print "ERROR: filename does not exist!"


