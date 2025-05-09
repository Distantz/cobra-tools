from generated.formats.path.compounds.PathExtrusion import PathExtrusion
from generated.formats.path.compounds.PathMaterial import PathMaterial
from generated.formats.path.compounds.PathResource import PathResource
from generated.formats.path.compounds.PathSupport import PathSupport
from generated.formats.path.compounds.PathType import PathType
from generated.formats.path.compounds.SupportSetRoot import SupportSetRoot
from generated.formats.path.compounds.LatticeSupportSetRoot import LatticeSupportSetRoot
from generated.formats.path.compounds.WoodenSupportSetRoot import WoodenSupportSetRoot
from generated.formats.path.compounds.PathJoinPartResourceRoot import PathJoinPartResourceRoot
from modules.formats.BaseFormat import MemStructLoader, MimeVersionedLoader


class PathExtrusionLoader(MemStructLoader):
	target_class = PathExtrusion
	extension = ".pathextrusion"


class PathMaterialLoader(MemStructLoader):
	target_class = PathMaterial
	extension = ".pathmaterial"

	def prep(self):
		# avoid generating pointers for these
		if not self.header.num_data:
			self.header.mat_data.data = None

	def create(self, file_path):
		self.header = self.target_class.from_xml_file(file_path, self.ovl.context)
		self.prep()
		self.write_memory_data()


class PathResourceLoader(MemStructLoader):
	target_class = PathResource
	extension = ".pathresource"


class PathJoinPartResourceLoader(MemStructLoader):
	target_class = PathJoinPartResourceRoot
	extension = ".pathjoinpartresource"

	def prep(self):
		# avoid generating pointers for these
		for res in self.header.resources_list.data:
			if not res.num_points_1:
				res.unk_points_1.data = None
			if not res.num_points_2:
				res.unk_points_2.data = None
			if not res.num_points_3:
				res.unk_points_3.data = None

	def create(self, file_path):
		self.header = self.target_class.from_xml_file(file_path, self.ovl.context)
		self.prep()
		self.write_memory_data()


class PathSupportLoader(MemStructLoader):
	target_class = PathSupport
	extension = ".pathsupport"

class PathTypeLoader(MemStructLoader):
	target_class = PathType
	extension = ".pathtype"


class SupportSetLoader(MimeVersionedLoader):
	target_class = SupportSetRoot
	extension = ".supportset"

	def prep(self):
		# avoid generating pointers for these
		if not self.header.num_connector_1:
			self.header.connector_1.data = None
		if not self.header.num_connector_2:
			self.header.connector_2.data = None

	# def collect(self):
	# 	super().collect()
	# 	print(self.header)

	def create(self, file_path):
		self.header = self.target_class.from_xml_file(file_path, self.ovl.context)
		self.prep()
		self.write_memory_data()

class LatticeSupportSetLoader(MemStructLoader):
	target_class = LatticeSupportSetRoot
	extension = ".latticesupportset"

	def prep(self):
		pass

	def create(self, file_path):
		self.header = self.target_class.from_xml_file(file_path, self.ovl.context)
		self.prep()
		self.write_memory_data()

class WoodenSupportSetLoader(MemStructLoader):
	target_class = WoodenSupportSetRoot
	extension = ".woodensupportset"

	def prep(self):
		pass

	def create(self, file_path):
		self.header = self.target_class.from_xml_file(file_path, self.ovl.context)
		self.prep()
		self.write_memory_data()

