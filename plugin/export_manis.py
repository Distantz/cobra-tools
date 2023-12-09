import logging
import os

import bpy
import mathutils

from generated.formats.base.basic import Ushort, Ubyte
from generated.formats.manis import ManisFile
from generated.formats.manis.compounds.ManiBlock import ManiBlock
from generated.formats.wsm.compounds.WsmHeader import WsmHeader
from modules.formats.shared import djb2
from plugin.modules_export.armature import get_armature
from plugin.utils.matrix_util import bone_name_for_ovl, get_scale_mat
from plugin.utils.transforms import ManisCorrector


def get_fcurves_by_type(group, dtype):
	return [fcurve for fcurve in group.channels if fcurve.data_path.endswith(dtype)]


def get_groups_for_type(b_action, dtype):
	out = {}
	for group in b_action.groups:
		# if group.name in bones_lut:
		fcurves = get_fcurves_by_type(group, dtype)
		if fcurves:
			out[group] = fcurves
	return out


def index_min_max(indices):
	if indices:
		return min(indices), max(indices)
	return 255, 0


def set_mani_info_counts(mani_info, b_action, bones_lut, m_dtype, b_dtype):
	groups = get_groups_for_type(b_action, b_dtype)
	groups = [group for group in groups if group.name in bones_lut]
	count = len(groups)
	for s in (f"{m_dtype}_bone_count", f"{m_dtype}_bone_count_repeat", f"{m_dtype}_bone_count_related"):
		setattr(mani_info, s, count)
	indices = [bones_lut[group.name] for group in groups]
	for s, v in zip((f"{m_dtype}_bone_min", f"{m_dtype}_bone_max"), index_min_max(indices)):
		setattr(mani_info, s, v)
	return groups, indices


def update_key_indices(k, m_dtype, groups, indices, target_names, bone_names):
	b_names = [group.name for group in groups]
	m_names = [bone_name_for_ovl(name) for name in b_names]
	target_names.update(m_names)
	getattr(k, f"{m_dtype}_bones_names")[:] = m_names
	# map key data index to bone
	getattr(k, f"{m_dtype}_channel_to_bone")[:] = indices
	# map bones to key data index
	if indices:
		bone_0 = min(indices)
		bone_1 = max(indices) + 1
		key_lut = {name: i for i, name in enumerate(b_names)}
		getattr(k, f"{m_dtype}_bone_to_channel")[:] = [key_lut.get(name, 255) for name in bone_names[bone_0:bone_1]]


def get_local_bone(bone):
	if bone.parent:
		return bone.parent.matrix_local.inverted() @ bone.matrix_local
	return bone.matrix_local


def export_wsm(corrector, b_action, folder, mani_info, bone_name, bones_data):
	wsm_name = f"{mani_info.name}_{bone_name}.wsm"
	wsm_path = os.path.join(folder, wsm_name)
	group = b_action.groups.get(bone_name)
	if group:
		loc_fcurves = get_fcurves_by_type(group, "location")
		rot_fcurves = get_fcurves_by_type(group, "rotation_quaternion")
		if loc_fcurves and rot_fcurves:
			logging.info(f"Exporting {wsm_name} to {wsm_path}")
			wsm = WsmHeader(mani_info.context)
			wsm.duration = mani_info.duration
			wsm.frame_count = mani_info.frame_count
			wsm.unknowns[6] = 1.0
			wsm.reset_field("locs")
			wsm.reset_field("quats")
			# print(wsm)
			bonerestmat = bones_data[group.name]
			for frame_i, key in enumerate(wsm.locs.data):
				v = mathutils.Vector([fcu.evaluate(frame_i) for fcu in loc_fcurves])
				v = mathutils.Matrix.Translation(v)
				# equivalent: multiply by rest rot and then add rest loc
				v = bonerestmat @ v
				key.x, key.y, key.z = corrector.blender_bind_to_nif_bind(v).to_translation()
			for frame_i, key in enumerate(wsm.quats.data):
				# sample frame
				q_m = mathutils.Quaternion([fcu.evaluate(frame_i) for fcu in rot_fcurves]).to_matrix().to_4x4()
				# add local rest transform
				final_m = bonerestmat @ q_m
				final_m = corrector.blender_bind_to_nif_bind(final_m)
				key.w, key.x, key.y, key.z = final_m.to_quaternion()
			with WsmHeader.to_xml_file(wsm, wsm_path):
				pass


def save(filepath=""):
	folder, manis_name = os.path.split(filepath)
	scene = bpy.context.scene
	bones_data = {}
	b_armature_ob = get_armature(scene)
	if not b_armature_ob:
		logging.warning(f"No armature was found in scene '{scene.name}' - did you delete it?")
	else:
		for bone in b_armature_ob.data.bones:
			bones_data[bone.name] = get_local_bone(bone)

	root_name = "def_c_root_joint"
	srb_name = "srb"

	corrector = ManisCorrector(False)
	mani = ManisFile()
	# hardcode for PZ for now, but it does not make a difference outside of compressed keys
	mani.version = 260
	target_names = set()
	try:
		bones_lut = {pose_bone.name: pose_bone["index"] for pose_bone in b_armature_ob.pose.bones}
	except:
		raise AttributeError(
			f"Some bones in {b_armature_ob.name} don't have the custom property 'index'.\n"
			f"Assign a unique index to all bones by exporting and importing the ms2 again.")
	# remove srb from bones_lut for JWE2, so it exported to wsm only
	if scene.cobra.version == 52:
		bones_lut.pop(srb_name, None)
	bone_names = [pose_bone.name for pose_bone in sorted(b_armature_ob.pose.bones, key=lambda pb: pb["index"])]
	action_names = [b_action.name for b_action in bpy.data.actions]
	mani.mani_count = len(action_names)
	mani.names[:] = action_names
	mani.reset_field("mani_infos")
	mani.reset_field("keys_buffer")
	for b_action, mani_info in zip(bpy.data.actions, mani.mani_infos):
		logging.info(f"Exporting {b_action.name}")
		mani_info.name = b_action.name
		mani_info.frame_count = int(round(b_action.frame_range[1] - b_action.frame_range[0]))
		# assume fps = 30
		# mani_info.duration = mani_info.frame_count / scene.render.fps
		mani_info.duration = mani_info.frame_count / 30.0
		mani_info.count_a = mani_info.count_b = 255
		mani_info.target_bone_count = len(b_armature_ob.pose.bones)

		export_wsm(corrector, b_action, folder, mani_info, srb_name, bones_data)

		pos_groups, pos_indices = set_mani_info_counts(mani_info, b_action, bones_lut, "pos", "location")
		# todo - fallback for eulers
		ori_groups, ori_indices = set_mani_info_counts(mani_info, b_action, bones_lut, "ori", "quaternion")
		scl_groups, scl_indices = set_mani_info_counts(mani_info, b_action, bones_lut, "scl", "scale")
		# mani_info.scl_bone_count_related = mani_info.scl_bone_count_repeat = 0
		floats = []
		bone_dtype = Ushort if mani_info.dtype.use_ushort else Ubyte
		mani_info.keys = ManiBlock(mani_info.context, mani_info, bone_dtype)
		k = mani_info.keys
		update_key_indices(k, "pos", pos_groups, pos_indices, target_names, bone_names)
		update_key_indices(k, "ori", ori_groups, ori_indices, target_names, bone_names)
		update_key_indices(k, "scl", scl_groups, scl_indices, target_names, bone_names)
		mani_info.root_pos_bone = mani_info.root_ori_bone = 255
		for bone_i, group in enumerate(pos_groups):
			logging.info(f"Exporting loc '{group.name}'")
			bonerestmat = bones_data[group.name]
			if group.name == root_name:
				mani_info.root_pos_bone = bone_i
			fcurves = get_fcurves_by_type(group, "location")
			fcurves_scale = get_fcurves_by_type(group, "scale")
			for frame_i, frame in enumerate(k.pos_bones):
				key = frame[bone_i]
				# translation is stored relative to the parent
				# whereas blender stores translation relative to the bone itself, not the parent
				v = mathutils.Vector([fcu.evaluate(frame_i) for fcu in fcurves])
				v = mathutils.Matrix.Translation(v)
				# equivalent: multiply by rest rot and then add rest loc
				v = bonerestmat @ v
				v = sample_scale(fcurves_scale, frame_i, inverted=True) @ v
				key.x, key.y, key.z = corrector.blender_bind_to_nif_bind(v).to_translation()
		for bone_i, group in enumerate(ori_groups):
			logging.info(f"Exporting rot '{group.name}'")
			if group.name == root_name:
				mani_info.root_ori_bone = bone_i
			bonerestmat = bones_data[group.name]
			fcurves = get_fcurves_by_type(group, "quaternion")
			for frame_i, frame in enumerate(k.ori_bones):
				key = frame[bone_i]
				# sample frame
				q_m = mathutils.Quaternion([fcu.evaluate(frame_i) for fcu in fcurves]).to_matrix().to_4x4()
				# add local rest transform
				final_m = bonerestmat @ q_m
				final_m = corrector.blender_bind_to_nif_bind(final_m)
				key.w, key.x, key.y, key.z = final_m.to_quaternion()
		for bone_i, group in enumerate(scl_groups):
			logging.info(f"Exporting scale '{group.name}'")
			fcurves = get_fcurves_by_type(group, "scale")
			for frame_i, frame in enumerate(k.scl_bones):
				key = frame[bone_i]
				scale_mat = sample_scale(fcurves, frame_i)
				# needs axis correction, but appears to be stored relative to the animated bone's axes
				scale_mat = corrector.blender_bind_to_nif_bind(scale_mat)
				# swizzle
				key.z, key.y, key.x = scale_mat.to_scale()
			# no support for shear in blender bones, so set to neutral
			# shear must not be 0.0
			for frame in k.shr_bones:
				key = frame[bone_i]
				key.y = 1.0
				key.x = 1.0
		print(mani_info)
		# print(mani_info.keys)
	mani.header.mani_files_size = mani.mani_count * 16
	mani.header.hash_block_size = len(target_names) * 4
	mani.reset_field("name_buffer")
	mani.name_buffer.bone_names[:] = sorted(target_names)
	mani.name_buffer.bone_hashes[:] = [djb2(name.lower()) for name in mani.name_buffer.bone_names]
	mani.save(filepath)
	return f"Finished manis export",


def sample_scale(fcurves, frame_i, inverted=False):
	if fcurves:
		v = mathutils.Vector([fcu.evaluate(frame_i) for fcu in fcurves])
	else:
		v = mathutils.Vector((1, 1, 1))
	# this inversion is apparently not equivalent to a real matrix inversion
	if inverted:
		try:
			v = mathutils.Vector((1 / v.x, 1 / v.y, 1 / v.z))
		except:
			logging.exception(f"Could not invert {v} at {frame_i} for {fcurves}")
	# v = mathutils.Matrix.Translation(v)
	scale_mat = get_scale_mat(v)
	return scale_mat
