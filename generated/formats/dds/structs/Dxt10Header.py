from generated.base_struct import BaseStruct
from generated.formats.dds.basic import Uint
from generated.formats.dds.enums.D3D10ResourceDimension import D3D10ResourceDimension
from generated.formats.dds.enums.DxgiFormat import DxgiFormat


class Dxt10Header(BaseStruct):

	__name__ = 'DXT10Header'

	_import_key = 'dds.structs.Dxt10Header'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.dxgi_format = DxgiFormat(self.context, 0, None)
		self.resource_dimension = D3D10ResourceDimension(self.context, 0, None)
		self.misc_flag = 0
		self.array_size = 1
		self.misc_flag_2 = 0
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'dxgi_format', DxgiFormat, (0, None), (False, None)
		yield 'resource_dimension', D3D10ResourceDimension, (0, None), (False, None)
		yield 'misc_flag', Uint, (0, None), (False, None)
		yield 'array_size', Uint, (0, None), (False, 1)
		yield 'misc_flag_2', Uint, (0, None), (False, None)
