from generated.formats.base.basic import Uint
from generated.formats.ovl_base.compounds.MemStruct import MemStruct


class Mipmap(MemStruct):

	"""
	Describes one tex mipmap
	"""

	__name__ = 'Mipmap'

	_import_key = 'tex.compounds.Mipmap'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# starting offset into the texture buffer for this mip level
		self.offset = 0

		# bytes for one array entry
		self.size = 0

		# bytes for all array entries
		self.size_array = 0

		# size of a scan line of blocks, including padding that is added to the end of the line
		self.size_scan = 0

		# size of the non-empty scanline blocks, ie. the last lods add empty scanlines as this is smaller than size
		self.size_data = 0
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'offset', Uint, (0, None), (False, None)
		yield 'size', Uint, (0, None), (False, None)
		yield 'size_array', Uint, (0, None), (False, None)
		yield 'size_scan', Uint, (0, None), (False, None)
		yield 'size_data', Uint, (0, None), (False, None)
