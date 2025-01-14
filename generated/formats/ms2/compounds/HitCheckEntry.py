from generated.base_struct import BaseStruct
from generated.formats.base.basic import Uint
from generated.formats.base.basic import Ushort
from generated.formats.ms2.compounds.BoundingBox import BoundingBox
from generated.formats.ms2.compounds.Capsule import Capsule
from generated.formats.ms2.compounds.ConvexHull import ConvexHull
from generated.formats.ms2.compounds.Cylinder import Cylinder
from generated.formats.ms2.compounds.MeshCollision import MeshCollision
from generated.formats.ms2.compounds.Sphere import Sphere
from generated.formats.ms2.enums.CollisionType import CollisionType


class HitCheckEntry(BaseStruct):

	__name__ = 'HitCheck Entry'

	_import_key = 'ms2.compounds.HitCheckEntry'

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.dtype = CollisionType(self.context, 0, None)

		# 0
		self.flag_0 = 0

		# JWE1: 16, PZ, JWE2: 0
		self.flag_1 = 0

		# JWE1: 564267, PZ: seen 17 and 22, JWE2: 34, 30
		self.flag_2 = 0

		# JWE1: 46, PZ: same as above, JWE2: 21, 27
		self.flag_3 = 0

		# ?
		self.zero_extra_pc_unk = 0

		# offset into joint names
		self.name_offset = 0
		self.collider = MeshCollision(self.context, 0, None)

		# ?
		self.zero_extra_zt = 0
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'dtype', CollisionType, (0, None), (False, None)
		yield 'flag_0', Ushort, (0, None), (False, None)
		yield 'flag_1', Ushort, (0, None), (False, None)
		yield 'flag_2', Uint, (0, None), (False, None)
		yield 'flag_3', Uint, (0, None), (False, None)
		if instance.context.version < 47:
			yield 'zero_extra_pc_unk', Uint, (0, None), (False, None)
		yield 'name_offset', Uint, (0, None), (False, None)
		if instance.dtype == 0:
			yield 'collider', Sphere, (0, None), (False, None)
		if instance.dtype == 1:
			yield 'collider', BoundingBox, (0, None), (False, None)
		if instance.dtype == 2:
			yield 'collider', Capsule, (0, None), (False, None)
		if instance.dtype == 3:
			yield 'collider', Cylinder, (0, None), (False, None)
		if instance.dtype == 7:
			yield 'collider', ConvexHull, (0, None), (False, None)
		if instance.dtype == 8:
			yield 'collider', ConvexHull, (0, None), (False, None)
		if instance.dtype == 10:
			yield 'collider', MeshCollision, (0, None), (False, None)
		if instance.context.version == 13:
			yield 'zero_extra_zt', Uint, (0, None), (False, None)
