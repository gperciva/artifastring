import bpy

# some computers need this, some don't.  No clue why.  :(
import sys
sys.path.append('.')

if '--' not in sys.argv:
	custom_argv = [] # as if no args are passed
else:
	custom_argv = sys.argv[sys.argv.index('--')+1: ] # get all args after "--"
print (custom_argv)

import violin
import parse_actions

### setup rending variables
render = bpy.context.scene.render
render.fps = 25
render.resolution_x = 640
render.resolution_y = 480
render.file_format = 'TARGA'
render.parts_x = 1
render.parts_y = 1
render.use_antialiasing = False
render.use_color_management = False
render.use_compositing = False
render.use_envmaps = False
render.use_motion_blur = False
render.use_raytrace = False
render.use_sequencer = False
render.use_shadows = False
render.use_sss = False
render.use_textures = False
render.use_simplify = True

bpy.context.scene.use_gravity = False

### setup model data
violin = violin.Violin()
#violin.debug()
#violin.bow.debug()

frame_end = parse_actions.load_keyframes(violin, "unit.actions", render.fps)
bpy.context.scene.frame_end = frame_end

# testing
#bpy.context.scene.frame_end = 10
#for i in range(10):
#	for st in range(4):
#		violin.finger_action(st, 0.1*i, i)
	#violin.bow_action(i%4, 0.05*i, 0.1, 0.1*i, i)
#	violin.bow_action((i-1)%4, 0.05, 0.1, 0.1*i, i)


