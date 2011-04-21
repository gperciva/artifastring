
import bpy
import abstract_object

import math

class Finger(abstract_object.AbstractObject):
	def __init__(self, violin, string_number):
		abstract_object.AbstractObject.__init__(self)
		self.violin = violin
		self.st = string_number

		self.obj = self.make_finger()
		self.set_visible(True)

	def make_finger(self):
		bpy.ops.mesh.primitive_cone_add(radius=0.1, depth=0.2)
		obj = bpy.data.objects["Cone"]
		obj.name = "finger_%i" % self.st
		finger_material = bpy.data.materials.new("finger_material")
		finger_material.diffuse_color = (1.0, 0.5, 0.0)
		obj.active_material = finger_material
		# TODO: bad rotation!
		obj.rotation_euler = math.pi * self.violin.towards_frog
		# parent on violin, due to animation ?
		obj.parent = self.violin.obj
		return obj


	def move(self, finger_position, frame):
		# TODO: iffy?  want to disable linear interpolation for
		# the next keyframe.
		if frame > 0:
			self.obj.keyframe_insert("location", frame=frame-1)
		#
		pos = 1.0 - finger_position
		# set properties and animation
		self.obj.location = self.violin.string_contact(self.st, pos)
		self.obj.keyframe_insert("location", frame=frame)


