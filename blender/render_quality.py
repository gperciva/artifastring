import bpy

def setup(quality, fps):
    ### unified settings
    render = bpy.context.scene.render
    render.fps = fps

    render.image_settings.file_format = 'TARGA'
    render.parts_x = 1
    render.parts_y = 1
    # HDTV 720p resolution
    render.resolution_x = 1280
    render.resolution_y = 720
    if quality==2:
        render.resolution_percentage = 100
    elif quality == 1:
        render.resolution_percentage = 50
    else:
        # VGA resolution
        render.resolution_percentage = 50
    # other options
    if quality < 2:
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

