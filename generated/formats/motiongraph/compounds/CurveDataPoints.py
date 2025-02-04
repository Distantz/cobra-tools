from generated.array import Array
from generated.formats.motiongraph.compounds.CurveDataPoint import CurveDataPoint
from generated.formats.ovl_base.compounds.MemStruct import MemStruct


class CurveDataPoints(MemStruct):

	"""
	array
	"""

	__name__ = 'CurveDataPoints'

	_import_key = 'motiongraph.compounds.CurveDataPoints'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = Array(self.context, 0, None, (0,), CurveDataPoint)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data', Array, (0, None, (instance.arg,), CurveDataPoint), (False, None)
