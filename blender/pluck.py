
import bpy
import abstract_object

import math

class Pluck(abstract_object.AbstractObject):
	def __init__(self, violin):
		abstract_object.AbstractObject.__init__(self)
		self.violin = violin

		self.size = self.violin.string_length

		self.obj = self.make_pluck()
		self.set_visible(False)

	def make_pluck(self):
		bpy.ops.mesh.primitive_cone_add(radius=0.01*self.size,
			depth=0.02*self.size)
		obj = bpy.context.active_object
		obj.name = "pluck"
		pluck_material = bpy.data.materials.new("pluck_material")
		pluck_material.diffuse_color = (1.0, 0.0, 0.5)
		obj.active_material = pluck_material
		# TODO: bad rotation!
		obj.rotation_euler = math.pi * self.violin.towards_frog
		# parent on violin, due to animation ?
		obj.parent = self.violin.obj
		return obj


	def move(self, string_number, pluck_position, frame):
		# animation
		self.obj.location = self.violin.string_contact(
			string_number, pluck_position)
		self.obj.keyframe_insert("location", frame=frame)
		# extra
		self.pluck_raise(frame)

	def pluck_raise(self, frame_start):
		off_target = 0.1*self.size
		for i in range(1,10):
			off_string = off_target * (1.0 - 0.9**i)
			#self.pluck_action(string_number, pluck_position, frame_start+i, off_string)
			# animation
			self.obj.location += off_string * self.violin.away_from_string
			self.obj.keyframe_insert("location", frame=frame_start+i)


