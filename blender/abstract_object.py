
class AbstractObject():
	def __init__(self):
		self.visible = None
		self.obj = None

	def set_visible(self, visible, frame=0):
		if self.visible != visible:
			self.visible = visible
			self.obj.hide = not visible
			self.obj.hide_render = not visible
			self.obj.keyframe_insert("hide", frame=frame)
			self.obj.keyframe_insert("hide_render", frame=frame)


