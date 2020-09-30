class Vector4:

	"""
	A vector in 3D space (x,y,z).
	"""

	# First coordinate.
	x: float

	# Second coordinate.
	y: float

	# Third coordinate.
	z: float

	# zeroth coordinate.
	w: float

	def __init__(self, arg=None, template=None):
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.x = 0
		self.y = 0
		self.z = 0
		self.w = 0

	def read(self, stream):

		io_start = stream.tell()
		self.x = stream.read_float()
		self.y = stream.read_float()
		self.z = stream.read_float()
		self.w = stream.read_float()

		self.io_size = stream.tell() - io_start

	def write(self, stream):

		io_start = stream.tell()
		stream.write_float(self.x)
		stream.write_float(self.y)
		stream.write_float(self.z)
		stream.write_float(self.w)

		self.io_size = stream.tell() - io_start

	def __repr__(self):
		s = 'Vector4 [Size: '+str(self.io_size)+']'
		s += '\n	* x = ' + self.x.__repr__()
		s += '\n	* y = ' + self.y.__repr__()
		s += '\n	* z = ' + self.z.__repr__()
		s += '\n	* w = ' + self.w.__repr__()
		s += '\n'
		return s

	def __str__(self):
		return "[ %6.3f %6.3f %6.3f %6.3f ]"%(self.x, self.y, self.z, self.w)
