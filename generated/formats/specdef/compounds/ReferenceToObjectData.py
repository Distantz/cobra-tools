from generated.formats.base.basic import Uint
from generated.formats.base.basic import ZString
from generated.formats.ovl_base.compounds.MemStruct import MemStruct
from generated.formats.ovl_base.compounds.Pointer import Pointer


class ReferenceToObjectData(MemStruct):

	"""
	16 bytes in log
	"""

	__name__ = 'ReferenceToObjectData'

	_import_key = 'specdef.compounds.ReferenceToObjectData'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ioptional = 0
		self.obj_name = Pointer(self.context, 0, ZString)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'obj_name', Pointer, (0, ZString), (False, None)
		yield 'ioptional', Uint, (0, None), (False, None)
