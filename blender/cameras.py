import bpy
import mathutils

def cycle_cameras(cycle_seconds, frame_end, fps):
    cameras = list(filter(lambda obj_key: obj_key.startswith("Camera"),
        bpy.data.objects.keys()))
    camera_locations = list(
        map(lambda cam: mathutils.Vector(bpy.data.objects.get(cam).location),
            cameras))
    camera_rotations = list(
        map(lambda cam: mathutils.Euler(bpy.data.objects.get(cam).rotation_euler),
            cameras))
    
    for i in range( int((frame_end/fps)/cycle_seconds) ):
        frame_num = i*cycle_seconds*fps
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
    

