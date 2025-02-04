import numpy
from generated.array import Array
from generated.base_struct import BaseStruct
from generated.formats.base.basic import Ushort


class InfoZTMemPool(BaseStruct):

	__name__ = 'InfoZTMemPool'

	_import_key = 'ms2.compounds.InfoZTMemPool'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# ?
		self.unk_count = 0

		# ?
		self.unks = Array(self.context, 0, None, (0,), Ushort)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unk_count', Ushort, (0, None), (False, None)
		yield 'unks', Array, (0, None, (instance.unk_count, 2,), Ushort), (False, None)
