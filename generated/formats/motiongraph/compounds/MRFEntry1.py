from generated.formats.ovl_base.compounds.MemStruct import MemStruct
from generated.formats.ovl_base.compounds.Pointer import Pointer


class MRFEntry1(MemStruct):

	"""
	8 bytes
	"""

	__name__ = 'MRFEntry1'

	_import_key = 'motiongraph.compounds.MRFEntry1'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.value = Pointer(self.context, 0, MRFEntry1._import_map["motiongraph.compounds.MRFMember1"])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'value', Pointer, (0, MRFEntry1._import_map["motiongraph.compounds.MRFMember1"]), (False, None)
