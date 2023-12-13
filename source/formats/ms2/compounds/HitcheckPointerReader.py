# START_GLOBALS
import logging

from generated.formats.ms2.compounds.HitCheck import HitCheck
from generated.base_struct import BaseStruct

# END_GLOBALS

class HitcheckPointerReader(BaseStruct):


	# START_CLASS

	def __init__(self, context, arg=None, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		pass

	@classmethod
	def read_fields(cls, stream, instance):
		joint_data = instance.arg
		instance.hc_pointers = []
		for jointinfo in joint_data.joint_infos:
			for i in range(jointinfo.hitcheck_count):
				hc = stream.read(8)
				instance.hc_pointers.append(hc)

	@classmethod
	def write_fields(cls, stream, instance):
		# joint_data = instance.arg
		# instance.hc_pointers = []
		for hcp in instance.hc_pointers:
			stream.write(hcp)

	@classmethod
	def get_fields_str(cls, instance, indent=0):
		try:
			s = ''
			joint_data = instance.arg
			for jointinfo in joint_data.joint_infos:
				s += str(jointinfo.hitchecks)
			return s
		except:
			return "Bad arg?"

