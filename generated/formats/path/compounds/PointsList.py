from generated.array import Array
from generated.formats.ovl_base.compounds.MemStruct import MemStruct
from generated.formats.path.compounds.Vector3 import Vector3


class PointsList(MemStruct):

	__name__ = 'PointsList'

	_import_key = 'path.compounds.PointsList'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.points = Array(self.context, 0, None, (0,), Vector3)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'points', Array, (0, None, (instance.arg,), Vector3), (False, None)
