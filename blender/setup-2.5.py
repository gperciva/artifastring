import bpy

# some computers need this, some don't.  No clue why.  :(
import sys
sys.path.append('.')

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


