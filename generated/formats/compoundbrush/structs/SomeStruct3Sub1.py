from generated.formats.compoundbrush.imports import name_type_map
from generated.formats.ovl_base.compounds.MemStruct import MemStruct


class SomeStruct3Sub1(MemStruct):

	__name__ = 'SomeStruct3_SUB1'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_1_count = name_type_map['Uint'](self.context, 0, None)
		self.unknown_1_float = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_1_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_1_float', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_1_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_1_float', name_type_map['Float'], (0, None), (False, None)
