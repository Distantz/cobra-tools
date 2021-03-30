import typing
from generated.array import Array


class InfoZTHeaderEntry:

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.unk_count = 0
		self.unks = Array()

	def read(self, stream):

		self.io_start = stream.tell()
		self.unk_count = stream.read_ushort()
		self.unks = stream.read_ushorts((self.unk_count, 2))

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_ushort(self.unk_count)
		stream.write_ushorts(self.unks)

		self.io_size = stream.tell() - self.io_start

	def get_info_str(self):
		return f'InfoZTHeaderEntry [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self):
		s = ''
		s += f'\n	* unk_count = {self.unk_count.__repr__()}'
		s += f'\n	* unks = {self.unks.__repr__()}'
		return s

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return s