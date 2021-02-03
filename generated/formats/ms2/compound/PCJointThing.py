import typing
from generated.array import Array


class PCJointThing:

	"""
	8 bytes
	"""

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0

		# -1
		self.shorts = Array()

	def read(self, stream):

		self.io_start = stream.tell()
		self.shorts = stream.read_shorts((4))

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_shorts(self.shorts)

		self.io_size = stream.tell() - self.io_start

	def get_info_str(self):
		return f'PCJointThing [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self):
		s = ''
		s += f'\n	* shorts = {self.shorts.__repr__()}'
		return s

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return s