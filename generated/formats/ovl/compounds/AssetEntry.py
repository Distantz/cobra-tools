from generated.base_struct import BaseStruct
from generated.formats.base.basic import Uint


class AssetEntry(BaseStruct):

	"""
	refers to root entries so they can be grouped into set entries.
	It seems to point exclusively to RootEntry's whose Ext Hash is FF FF FF FF aka max uint32
	"""

	__name__ = 'AssetEntry'

	_import_key = 'ovl.compounds.AssetEntry'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.file_hash = 0
		self.zero_0 = 0
		self.ext_hash = 0
		self.zero_1 = 0

		# index into root entries array; hash of targeted file matches this assetentry's hash.
		self.file_index = 0
		self.zero_2 = 0
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_hash', Uint, (0, None), (False, None)
		yield 'zero_0', Uint, (0, None), (False, None)
		if instance.context.version >= 19:
			yield 'ext_hash', Uint, (0, None), (False, None)
			yield 'zero_1', Uint, (0, None), (False, None)
		yield 'file_index', Uint, (0, None), (False, None)
		yield 'zero_2', Uint, (0, None), (False, None)
