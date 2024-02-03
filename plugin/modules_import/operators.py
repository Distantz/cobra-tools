import os
import bpy.utils.previews
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper

from plugin import import_banis, import_manis, import_matcol, import_fgm, import_ms2, import_spl, import_voxelskirt
from plugin.utils.matrix_util import handle_errors


class ImportBanis(bpy.types.Operator, ImportHelper):
    """Import from Cobra baked animations file format (.banis)"""
    bl_idname = "import_scene.cobra_banis"
    bl_label = 'Import Banis'
    bl_options = {'UNDO'}
    filename_ext = ".banis"
    filter_glob: StringProperty(default="*.banis", options={'HIDDEN'})
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    # set_fps = BoolProperty(name="Adjust FPS", description="Set the scene to FPS used by BANI", default=True)

    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob"))
        return import_banis.load(**keywords)


class ImportManis(bpy.types.Operator, ImportHelper):
    """Import from Cobra animations file format (.manis)"""
    bl_idname = "import_scene.cobra_manis"
    bl_label = 'Import Manis'
    bl_options = {'UNDO'}
    filename_ext = ".manis"
    filter_glob: StringProperty(default="*.manis", options={'HIDDEN'})
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    # set_fps = BoolProperty(name="Adjust FPS", description="Set the scene to FPS used by BANI", default=True)

    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob"))
        return import_manis.load(**keywords)


class ImportMatcol(bpy.types.Operator, ImportHelper):
    """Import from Matcol file format (.matcol, .dinosaurmateriallayers)"""
    bl_idname = "import_scene.cobra_matcol"
    bl_label = 'Import Matcol'
    bl_options = {'UNDO'}
    filename_ext = ".dinosaurmateriallayers"

    # filter_glob: StringProperty(default="*.matcol", options={'HIDDEN'})
    # filter_glob: StringProperty(default="*.matcol", options={'HIDDEN'})

    # filename_ext = ".x3d"
    # filter_glob: StringProperty(default="*.matcol;*.materialcollection;*.dinosaurmateriallayers", options={'HIDDEN'})

    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob"))
        return handle_errors(self, import_matcol.load, keywords)


class ImportFgm(bpy.types.Operator, ImportHelper):
    """Import from Fgm file format (.fgm)"""
    bl_idname = "import_scene.cobra_fgm"
    bl_label = 'Import Fgm'
    bl_options = {'UNDO'}
    filename_ext = ".fgm"
    filter_glob: StringProperty(default="*.fgm", options={'HIDDEN'})

    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob"))
        return handle_errors(self, import_fgm.load, keywords)


class ImportMS2(bpy.types.Operator, ImportHelper):
    """Import from MS2 file format (.MS2)"""
    bl_idname = "import_scene.cobra_ms2"
    bl_label = 'Import MS2'
    bl_options = {'UNDO'}
    filename_ext = ".ms2"
    filter_glob: StringProperty(default="*.ms2", options={'HIDDEN'})
    use_custom_normals: BoolProperty(name="Use MS2 Normals", description="Applies MS2 normals as custom normals to preserve the original shading. May crash on some meshes due to a blender bug",
                                     default=False)
    mirror_mesh: BoolProperty(name="Mirror Meshes", description="Mirrors models. Careful, sometimes bones don't match",
                              default=False)

    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob"))
        return handle_errors(self, import_ms2.load, keywords)


class ImportSPL(bpy.types.Operator, ImportHelper):
    """Import from spline file format (.spl)"""
    bl_idname = "import_scene.cobra_spl"
    bl_label = 'Import SPL'
    bl_options = {'UNDO'}
    filename_ext = ".spl"
    filter_glob: StringProperty(default="*.spl", options={'HIDDEN'})

    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob"))
        return handle_errors(self, import_spl.load, keywords)


class ImportVoxelskirt(bpy.types.Operator, ImportHelper):
    """Import from Voxelskirt file format (.voxelskirt)"""
    bl_idname = "import_scene.cobra_voxelskirt"
    bl_label = 'Import Voxelskirt'
    bl_options = {'UNDO'}
    filename_ext = ".voxelskirt"
    filter_glob: StringProperty(default="*.voxelskirt", options={'HIDDEN'})

    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob"))
        return handle_errors(self, import_voxelskirt.load, keywords)


class ImportMS2FromBrowser(bpy.types.Operator):
    """Imports ms2 content as new scenes from the file browser"""
    bl_idname = "ct_wm.import_ms2"
    bl_label = "Import ms2"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        folder = context.space_data.params.directory.decode('ascii')
        file   = context.space_data.params.filename
        filepath = os.path.join(folder, file).replace("\\","/")
        print("Importing: " + filepath)
        handle_errors(self, import_ms2.load, { 'filepath': filepath } )
        return {'FINISHED'}

class ImportFGMFromBrowser(bpy.types.Operator):
    """Imports fgm as a new material from the file browser"""
    bl_idname = "ct_wm.import_fgm"
    bl_label = "Import fgm"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        folder = context.space_data.params.directory.decode('ascii')
        file   = context.space_data.params.filename
        filepath = os.path.join(folder, file).replace("\\","/")
        print("Importing: " + filepath)
        handle_errors(self, import_fgm.load, { 'filepath': filepath } )
        return {'FINISHED'}

