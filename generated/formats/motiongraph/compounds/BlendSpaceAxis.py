from generated.formats.base.basic import ZString
from generated.formats.ovl_base.compounds.MemStruct import MemStruct
from generated.formats.ovl_base.compounds.Pointer import Pointer


class BlendSpaceAxis(MemStruct):

	"""
	8 bytes
	"""

	__name__ = 'BlendSpaceAxis'

	_import_key = 'motiongraph.compounds.BlendSpaceAxis'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.variable_name = Pointer(self.context, 0, ZString)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'variable_name', Pointer, (0, ZString), (False, None)
