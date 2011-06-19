import bpy

# add modules in the script directory
import sys
import os.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


# get arguments after --
if '--' in sys.argv:
    custom_argv = sys.argv[sys.argv.index('--')+1: ]
else:
    custom_argv = []

import argparse
parser = argparse.ArgumentParser(
    prog = "artifastring-blender.py",
    description = """Generate a video from an .actions file.
    Options come after -- on the blender command-line.""",
    )

parser.add_argument('--fps', metavar='N', type=int,
    help="Frames per second", default=25)
parser.add_argument('-f', '--filename', metavar='FILENAME',
    help="Filename of .actions", required=True)
parser.add_argument('-q', '--quality', action="store_true",
    help="Use good quality", default=False)

args = parser.parse_args(custom_argv)

import violin
import parse_actions
import render_quality

### setup rending variables
render_quality.setup(args.quality, args.fps)

### setup model data
violin = violin.Violin()
#violin.debug()
#violin.bow.debug()

### process actions file
frame_end = parse_actions.load_keyframes(violin, args.filename, args.fps)
bpy.context.scene.frame_end = frame_end


