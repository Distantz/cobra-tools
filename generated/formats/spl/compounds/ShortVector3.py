from generated.formats.base.basic import Short
from generated.formats.ovl_base.compounds.MemStruct import MemStruct


class ShortVector3(MemStruct):

	"""
	A vector in 3D space (x,y,z).
	"""

	__name__ = 'ShortVector3'

	_import_key = 'spl.compounds.ShortVector3'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# First coordinate.
		self.x = 0

		# Second coordinate.
		self.y = 0

		# Third coordinate.
		self.z = 0
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'x', Short, (0, None), (False, None)
		yield 'y', Short, (0, None), (False, None)
		yield 'z', Short, (0, None), (False, None)
