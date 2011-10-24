import bpy
import mathutils

def cycle_cameras(cycle_seconds, frame_end, fps):
    num_cameras = len(bpy.data.cameras) -1 # don't count the active camera
    for i in range( int((frame_end/fps)/cycle_seconds) ):
        frame_num = i*cycle_seconds*fps
        now = i % num_cameras
        prev = (i-1) % num_cameras

        set_camera(now, prev, frame_num)


def set_camera(camera_number, prev, frame_num):
    cameras = list(filter(lambda obj_key: obj_key.startswith("Camera.0"),
        bpy.data.objects.keys()))
    cameras.sort() # just in case
    camera_locations = list(
        map(lambda cam: mathutils.Vector(bpy.data.objects.get(cam).location),
            cameras))
    camera_rotations = list(
        map(lambda cam: mathutils.Euler(bpy.data.objects.get(cam).rotation_euler),
            cameras))

    if frame_num > 0:
        bpy.context.scene.camera.rotation_euler = camera_rotations[prev]
        bpy.context.scene.camera.location = camera_locations[prev]
        bpy.context.scene.camera.keyframe_insert("rotation_euler", frame = (frame_num-1))
        bpy.context.scene.camera.keyframe_insert("location", frame = (frame_num-1))
    
    bpy.context.scene.camera.rotation_euler = camera_rotations[camera_number]
    bpy.context.scene.camera.location = camera_locations[camera_number]
    bpy.context.scene.camera.keyframe_insert("rotation_euler", frame = frame_num)
    bpy.context.scene.camera.keyframe_insert("location", frame = frame_num)


