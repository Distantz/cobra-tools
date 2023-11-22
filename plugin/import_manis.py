import logging
import math
import os
import time

import bpy
import mathutils

from generated.formats.manis import ManisFile
from generated.formats.wsm.compounds.WsmHeader import WsmHeader
from plugin.export_manis import get_local_bone
from plugin.modules_export.armature import get_armature
from plugin.modules_import.anim import Animation
from plugin.utils.matrix_util import bone_name_for_blender, get_scale_mat
from plugin.utils.object import create_ob
from plugin.utils.transforms import ManisCorrector

interp_loc = None
anim_sys = Animation()
dt_size = {
	"location": tuple(range(3)),
	"rotation_quaternion": tuple(range(4)),
	"scale": tuple(range(3)),
}


def iter_keys(m_bone_names, m_keys, bones_data, b_action, b_dtype, m_extra_bone_names=(), m_extra_keys=()):
	scale_lut = {name: i for i, name in enumerate(m_extra_bone_names)}
	for bone_i, m_name in enumerate(m_bone_names):
		b_name = bone_name_for_blender(m_name)
		logging.debug(f"Importing '{b_name}'")
		if b_name in bones_data:
			bonerestmat_inv = bones_data[b_name]
			b_channel = b_name
		else:
			# not sure this is desired like that
			if bones_data:
				logging.warning(f"Ignoring extraneous bone '{b_name}'")
				continue
			else:
				logging.debug(f"Object transform '{b_name}' as LocRotScale")
				bonerestmat_inv = mathutils.Matrix().to_4x4()
				b_channel = None

		scale_i = scale_lut.get(m_name, None)
		fcurves = anim_sys.create_fcurves(b_action, b_dtype, dt_size[b_dtype], None, b_channel)
		for frame_i, frame in enumerate(m_keys):
			key = frame[bone_i]
			if scale_i is not None:
				extra_key = m_extra_keys[frame_i][scale_i]
			else:
				extra_key = None
			yield frame_i, key, bonerestmat_inv, fcurves, extra_key, b_name


def import_wsm(corrector, b_action, folder, mani_info, bone_name, bones_data):
	wsm_name = f"{mani_info.name}_{bone_name}.wsm"
	wsm_path = os.path.join(folder, wsm_name)
	if os.path.isfile(wsm_path):
		logging.info(f"Importing {wsm_name}")
		wsm = WsmHeader.from_xml_file(wsm_path, mani_info.context)
		bonerestmat_inv = bones_data[bone_name]
		loc_fcurves = anim_sys.create_fcurves(b_action, "location", range(3), None, bone_name)
		for frame_i, key in enumerate(wsm.locs.data):
			key = mathutils.Vector(key)
			key = (bonerestmat_inv @ corrector.nif_bind_to_blender_bind(mathutils.Matrix.Translation(key))).to_translation()
			anim_sys.add_key(loc_fcurves, frame_i, key, interp_loc)
		rot_fcurves = anim_sys.create_fcurves(b_action, "rotation_quaternion", range(4), None, bone_name)
		for frame_i, key in enumerate(wsm.quats.data):
			key = mathutils.Quaternion([key.w, key.x, key.y, key.z])
			key = (bonerestmat_inv @ corrector.nif_bind_to_blender_bind(key.to_matrix().to_4x4())).to_quaternion()
			anim_sys.add_key(rot_fcurves, frame_i, key, interp_loc)


def load(files=[], filepath="", set_fps=False):
	folder, manis_name = os.path.split(filepath)
	starttime = time.time()
	corrector = ManisCorrector(False)
	scene = bpy.context.scene

	bones_data = {}
	b_armature_ob = get_armature(scene)
	if not b_armature_ob:
		logging.warning(f"No armature was found in scene '{scene.name}' - did you delete it?")
		b_cam_data = bpy.data.cameras.new("ManisCamera")
		b_armature_ob = create_ob(scene, "ManisCamera", b_cam_data)
		b_armature_ob.rotation_mode = "QUATERNION"
		cam_corr = mathutils.Euler((math.radians(90), 0, math.radians(-90))).to_quaternion()
	else:
		for p_bone in b_armature_ob.pose.bones:
			p_bone.rotation_mode = "QUATERNION"
		for bone in b_armature_ob.data.bones:
			bones_data[bone.name] = get_local_bone(bone).inverted()
		cam_corr = None
	manis = ManisFile()
	manis.load(filepath)

	for mi in manis.mani_infos:
		b_action = anim_sys.create_action(b_armature_ob, mi.name)
		print(mi)
		k = mi.keys
		if mi.dtype.compression != 0:
			logging.info(f"{mi.name} is compressed, trying to import anyway")
			b_action.use_frame_range = True
			b_action.frame_start = 0
			b_action.frame_end = mi.frame_count
			ck = k.compressed
			try:
				manis.decompress(None, mi)
			except:
				logging.exception(f"Decompressing {mi.name} failed, skipping")
				continue

			import_wsm(corrector, b_action, folder, mi, "srb", bones_data)

			for frame_i, key, bonerestmat_inv, fcurves, scale, b_name in iter_keys(
					k.pos_bones_names, ck.pos_bones, bones_data, b_action, "location"):  #, k.scl_bones_names, ck.scl_bones):
				#if frame_i % 32:
					#continue
				key = mathutils.Vector(key)
				# # correct for scale
				# if scale:
				# 	key = mathutils.Vector([key.x * scale.z, key.y * scale.y, key.z * scale.x])
				key = (bonerestmat_inv @ corrector.nif_bind_to_blender_bind(mathutils.Matrix.Translation(key))).to_translation()
				anim_sys.add_key(fcurves, frame_i, key, interp_loc)
			for frame_i, in_key, bonerestmat_inv, fcurves, _, b_name in iter_keys(
					k.ori_bones_names, ck.ori_bones, bones_data, b_action, "rotation_quaternion"):
				if frame_i % 32:
					continue
				key = mathutils.Quaternion([in_key[3], in_key[0], in_key[1], in_key[2]])
				# if frame_i == 0 and b_name == "def_c_hips_joint":
				# 	logging.info(f"{mi.name} {key}")
				key = (bonerestmat_inv @ corrector.nif_bind_to_blender_bind(key.to_matrix().to_4x4())).to_quaternion()
				# if cam_corr is not None:
				# 	out = mathutils.Quaternion(cam_corr)
				# 	out.rotate(key)
				# 	key = out
				anim_sys.add_key(fcurves, frame_i, key, interp_loc)
			# skip uncompressed anim
			continue
		logging.info(f"Importing '{mi.name}'")
		for frame_i, key, bonerestmat_inv, fcurves, scale, b_name in iter_keys(
				k.pos_bones_names, k.pos_bones, bones_data, b_action, "location", k.scl_bones_names, k.scl_bones):
			key = mathutils.Vector([key.x, key.y, key.z])
			# correct for scale
			if scale:
				key = mathutils.Vector([key.x * scale.z, key.y * scale.y, key.z * scale.x])
			key = (bonerestmat_inv @ corrector.nif_bind_to_blender_bind(mathutils.Matrix.Translation(key))).to_translation()
			anim_sys.add_key(fcurves, frame_i, key, interp_loc)
		for frame_i, key, bonerestmat_inv, fcurves, _, b_name in iter_keys(
				k.ori_bones_names, k.ori_bones, bones_data, b_action, "rotation_quaternion"):
			key = mathutils.Quaternion([key.w, key.x, key.y, key.z])
			# if frame_i == 0 and b_name == "def_c_hips_joint":
			# 	logging.info(f"{mi.name} {key}")
			key = (bonerestmat_inv @ corrector.nif_bind_to_blender_bind(key.to_matrix().to_4x4())).to_quaternion()
			if cam_corr is not None:
				out = mathutils.Quaternion(cam_corr)
				out.rotate(key)
				key = out
			anim_sys.add_key(fcurves, frame_i, key, interp_loc)
		for frame_i, key, bonerestmat_inv, fcurves, _, b_name in iter_keys(
				k.scl_bones_names, k.scl_bones, bones_data, b_action, "scale"):
			# swizzle
			key = mathutils.Vector([key.z, key.y, key.x])
			# correct axes
			mat = get_scale_mat(key)
			key = corrector.nif_bind_to_blender_bind(mat).to_scale()
			anim_sys.add_key(fcurves, frame_i, key, interp_loc)
		# these can vary in use according to the name of the channel
		for bone_i, m_name in enumerate(k.floats_names):
			b_name = bone_name_for_blender(m_name)
			logging.info(f"Importing '{b_name}'")
			# only known for camera
			if m_name == "CameraFOV":
				b_data_action = anim_sys.create_action(b_cam_data, f"{mi.name}Data")
				fcurves = anim_sys.create_fcurves(b_data_action, "lens", (0,))
				for frame_i, frame in enumerate(k.floats):
					key = frame[bone_i]
					anim_sys.add_key(fcurves, frame_i, (10 / key,), interp_loc)
			else:
				logging.warning(f"Don't know how to import floats for '{b_name}'")

	scene.frame_start = 0
	scene.frame_end = mi.frame_count
	scene.render.fps = int(round(mi.frame_count / mi.duration))
	return {'FINISHED'}
