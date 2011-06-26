import bpy

# add modules in the script directory
import sys
import os.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


def get_options():
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
    parser.add_argument("-q", "--quality", type=int,
        metavar="N", default=0,
        help="Quality of rending: 0 (terrible) to 2 (best)")

    args = parser.parse_args(custom_argv)
    return args

options = get_options()
    
import violin
import parse_actions
import render_quality

### setup rending variables
render_quality.setup(options.quality, options.fps)

### setup model data
violin = violin.Violin()
#violin.debug()
#violin.bow.debug()

### process actions file
frame_end = parse_actions.load_keyframes(violin, options.filename, options.fps)
bpy.context.scene.frame_end = frame_end


### switch between cameras
CAMERA_SWITCH_SECONDS = 6.0

import mathutils
cameras = list(filter(lambda obj_key: obj_key.startswith("Camera"),
    bpy.data.objects.keys()))
camera_locations = list(
    map(lambda cam: mathutils.Vector(bpy.data.objects.get(cam).location),
        cameras))
camera_rotations = list(
    map(lambda cam: mathutils.Euler(bpy.data.objects.get(cam).rotation_euler),
        cameras))

for i in range( int((frame_end/options.fps)/CAMERA_SWITCH_SECONDS) ):
    frame_num = i*CAMERA_SWITCH_SECONDS*options.fps
    now = i % len(bpy.data.cameras)
    prev = (i-1) % len(bpy.data.cameras)

    if frame_num > 0:
        bpy.context.scene.camera.rotation_euler = camera_rotations[prev]
        bpy.context.scene.camera.location = camera_locations[prev]
        bpy.context.scene.camera.keyframe_insert("rotation_euler", frame = (frame_num-1))
        bpy.context.scene.camera.keyframe_insert("location", frame = (frame_num-1))

    bpy.context.scene.camera.rotation_euler = camera_rotations[now]
    bpy.context.scene.camera.location = camera_locations[now]
    bpy.context.scene.camera.keyframe_insert("rotation_euler", frame = frame_num)
    bpy.context.scene.camera.keyframe_insert("location", frame = frame_num)


