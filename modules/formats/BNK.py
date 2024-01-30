import logging
import os
import shutil
from io import BytesIO

from generated.formats.bnk import BnkFile
from generated.formats.bnk.compounds.BnkBufferData import BnkBufferData
from modules.formats.BaseFormat import BaseFile


class BnkLoader(BaseFile):
	extension = ".bnk"

	def create(self, file_path):
		bnk_file = BnkFile()
		bnk_file.load(file_path)
		# ensure update of bnk_file.bnk_header.size_b
		if bnk_file.bnk_header.external_aux_b_count:
			bnk_file.bnk_header.size_b = os.path.getsize(bnk_file.aux_b_path)
			logging.debug(f"bnk_file.bnk_header.size_b = {bnk_file.bnk_header.size_b}")
		with BytesIO() as stream:
			BnkBufferData.to_stream(bnk_file.bnk_header, stream, self.context)
			buffers = [stream.getvalue(), ]
		if bnk_file.bnk_header.external_aux_b_count:
			logging.info(f"Loaded bnk {bnk_file.aux_b_name_bare} into OVL buffers")

			with open(bnk_file.aux_b_path, "rb") as f:
				buffers.append(f.read())

		# print(bnk_file)
		self.write_root_bytes(b"\x00" * 16)
		self.create_data_entry(buffers)
		self.aux_entries = []
		if bnk_file.bnk_header.external_b_suffix:
			self.aux_entries.append(bnk_file.bnk_header.external_b_suffix)
		if bnk_file.bnk_header.external_s_suffix:
			self.aux_entries.append(bnk_file.bnk_header.external_s_suffix)

	def get_aux_size(self, aux_basename):
		bnkpath = f"{self.ovl.path_no_ext}_{self.basename}_bnk_{aux_basename.lower()}.aux"
		if os.path.isfile(bnkpath):
			return os.path.getsize(bnkpath)
		else:
			logging.warning(f"Could not find {bnkpath} to update .aux file size")
			return 0

	def extract(self, out_dir):
		bnk_name = os.path.splitext(self.name)[0]
		out_path = out_dir(self.name)
		out_files = [out_path, ]
		buffer_datas = self.data_entry.buffer_datas
		main_buffer = buffer_datas[0]
		with open(out_path, "wb") as f:
			f.write(self.pack_header(b"BNK"))
			f.write(main_buffer)

		# only needed to assert validity of aux stream mapping
		with BytesIO(main_buffer) as stream:
			bnk_header = BnkBufferData.from_stream(stream, self.context)

		# ensure that aux files are where they should be
		for aux_suffix in self.aux_entries:
			aux_suffix = aux_suffix.lower()
			if aux_suffix == "b":
				assert bnk_header.external_b_suffix.lower() == "b"
			elif aux_suffix == "s":
				assert bnk_header.external_s_suffix.lower() == "s"
			else:
				logging.warning(f"Unknown .aux suffix '{aux_suffix}'")
				continue
			aux_name = f"{self.ovl.basename}_{bnk_name}_bnk_{aux_suffix}.aux"
			aux_path = os.path.join(self.ovl.dir, aux_name)
			if not os.path.isfile(aux_path):
				logging.error(f"External .aux file '{aux_suffix}' was not found at {aux_path}")
			# copy to tmp path so we leave the original file intact
			copy_aux_path = out_dir(aux_name)
			shutil.copy(aux_path, copy_aux_path)
			out_files.append(copy_aux_path)

		# check if an aux 'file' is stored as second buffer in ovl
		if len(buffer_datas) > 1:
			# always type b
			aux_name = f"{self.ovl.basename}_{bnk_name}_bnk_b.aux"
			# extract to tmp path
			aux_path = out_dir(aux_name)
			logging.debug(f"Extracted internal .aux to {aux_path}")
			out_files.append(aux_path)
			with open(aux_path, "wb") as f:
				for b in buffer_datas[1:]:
					f.write(b)
		return out_files

