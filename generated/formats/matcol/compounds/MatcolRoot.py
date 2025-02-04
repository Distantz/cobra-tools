from generated.formats.base.basic import Uint64
from generated.formats.ovl_base.compounds.MemStruct import MemStruct
from generated.formats.ovl_base.compounds.Pointer import Pointer


class MatcolRoot(MemStruct):

	"""
	root_entry data
	"""

	__name__ = 'MatcolRoot'

	_import_key = 'matcol.compounds.MatcolRoot'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# always 1
		self.one = 0
		self.main = Pointer(self.context, 0, MatcolRoot._import_map["matcol.compounds.RootFrag"])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'main', Pointer, (0, MatcolRoot._import_map["matcol.compounds.RootFrag"]), (False, None)
		yield 'one', Uint64, (0, None), (False, None)
