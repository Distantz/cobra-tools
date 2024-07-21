from generated.array import Array
from generated.base_struct import BaseStruct
from generated.formats.ms2.imports import name_type_map


class JointInfo(BaseStruct):

	"""
	#ARG# is the names buffer
	PC: 40 bytes
	the following defaults are all the same in PZ and JWE2 as of 2022-10-14
	"""

	__name__ = 'JointInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.eleven = name_type_map['Uint'].from_value(11)
		self.zero_0 = name_type_map['Int'].from_value(0)
		self.zero_1 = name_type_map['Int'].from_value(0)
		self.minus_1 = name_type_map['Int'].from_value(-1)
		self.minus_1_b_pc = name_type_map['Int'](self.context, 0, None)
		self.name = name_type_map['OffsetString'](self.context, self.context.joint_names, None)
		self.hitcheck_count = name_type_map['Uint'](self.context, 0, None)
		self.zero_2_a = name_type_map['Int'](self.context, 0, None)

		# 8 bytes of zeros
		self.zero_2 = name_type_map['Uint64'](self.context, 0, None)
		self.hitcheck_pointers = Array(self.context, 0, None, (0,), name_type_map['Uint64'])
		self.hitchecks = Array(self.context, self.arg, None, (0,), name_type_map['HitCheck'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'eleven', name_type_map['Uint'], (0, None), (False, 11), (None, None)
		yield 'zero_0', name_type_map['Int'], (0, None), (False, 0), (None, None)
		yield 'zero_1', name_type_map['Int'], (0, None), (False, 0), (None, None)
		yield 'minus_1', name_type_map['Int'], (0, None), (False, -1), (None, None)
		yield 'minus_1_b_pc', name_type_map['Int'], (0, None), (False, None), (lambda context: context.version <= 32, None)
		yield 'name', name_type_map['OffsetString'], (None, None), (False, None), (None, None)
		yield 'hitcheck_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero_2_a', name_type_map['Int'], (0, None), (False, None), (lambda context: context.version <= 32, None)
		yield 'zero_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'hitcheck_pointers', Array, (0, None, (None,), name_type_map['Uint64']), (False, None), (lambda context: context.version <= 32, None)
		yield 'hitcheck_pointers', Array, (0, None, (None,), name_type_map['Uint64']), (False, None), (lambda context: context.version >= 47, None)
		yield 'hitchecks', Array, (None, None, (None,), name_type_map['HitCheck']), (False, None), (lambda context: context.version <= 32, None)
		yield 'hitchecks', Array, (None, None, (None,), name_type_map['HitCheck']), (False, None), (lambda context: context.version >= 47, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'eleven', name_type_map['Uint'], (0, None), (False, 11)
		yield 'zero_0', name_type_map['Int'], (0, None), (False, 0)
		yield 'zero_1', name_type_map['Int'], (0, None), (False, 0)
		yield 'minus_1', name_type_map['Int'], (0, None), (False, -1)
		if instance.context.version <= 32:
			yield 'minus_1_b_pc', name_type_map['Int'], (0, None), (False, None)
		yield 'name', name_type_map['OffsetString'], (instance.context.joint_names, None), (False, None)
		yield 'hitcheck_count', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 32:
			yield 'zero_2_a', name_type_map['Int'], (0, None), (False, None)
		yield 'zero_2', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.version <= 32 and include_abstract:
			yield 'hitcheck_pointers', Array, (0, None, (instance.hitcheck_count,), name_type_map['Uint64']), (False, None)
		if instance.context.version >= 47:
			yield 'hitcheck_pointers', Array, (0, None, (instance.hitcheck_count,), name_type_map['Uint64']), (False, None)
		if instance.context.version <= 32 and include_abstract:
			yield 'hitchecks', Array, (instance.arg, None, (instance.hitcheck_count,), name_type_map['HitCheck']), (False, None)
		if instance.context.version >= 47:
			yield 'hitchecks', Array, (instance.arg, None, (instance.hitcheck_count,), name_type_map['HitCheck']), (False, None)
