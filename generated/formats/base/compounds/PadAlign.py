from generated.base_struct import BaseStruct
from modules.formats.shared import get_padding_size

ZERO = b"\x00"


from generated.base_struct import BaseStruct


class PadAlign(BaseStruct):

	"""
	Grabs as many bytes as needed to align #ARG# bytes from the start of #TEMPLATE#
	"""

	__name__ = 'PadAlign'

	_import_key = 'base.compounds.PadAlign'

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = b""

	def get_pad(self, stream):
		distance = stream.tell() - self.template.io_start
		return get_padding_size(distance, alignment=self.arg)

	def __repr__(self):
		return f"{self.data} Size: {len(self.data)}"

	@classmethod
	def read_fields(cls, stream, instance):
		instance.data = stream.read(instance.get_pad(stream))

	@classmethod
	def write_fields(cls, stream, instance):
		instance.data = ZERO * instance.get_pad(stream)
		stream.write(instance.data)

