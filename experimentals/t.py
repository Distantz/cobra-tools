# import sys
# from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout
# from PyQt5.QtGui import QIcon
#
#
# class App(QWidget):
#
#     def __init__(self):
#         super().__init__()
#         self.title = 'PyQt5 file system view - pythonspot.com'
#         self.left = 10
#         self.top = 10
#         self.width = 640
#         self.height = 480
#         self.initUI()
#
#     def initUI(self):
#         self.setWindowTitle(self.title)
#         self.setGeometry(self.left, self.top, self.width, self.height)
#
#         self.model = QFileSystemModel()
#         self.model.setRootPath('')
#         self.tree = QTreeView()
#         self.tree.setModel(self.model)
#
#         self.tree.setAnimated(False)
#         self.tree.setIndentation(20)
#         self.tree.setSortingEnabled(True)
#
#         self.tree.setWindowTitle("Dir View")
#         self.tree.resize(640, 480)
#
#         windowLayout = QVBoxLayout()
#         windowLayout.addWidget(self.tree)
#         self.setLayout(windowLayout)
#
#         self.show()
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = App()
#     sys.exit(app.exec_())

#
# import os
#
#
# def increment_strip(fp, increment=5):
#     bp, ext = os.path.splitext(fp)
#     with open(fp, "rb") as f:
#         d = f.read()
#
#     for i in range(increment):
#         with open(f"{bp}_{i}_strip{ext}", "wb") as fo:
#             fo.write(d[i:].rstrip(b"x\00"))
#         with open(f"{bp}_{i}{ext}", "wb") as fo:
#             fo.write(d[i:])
#
#
# # increment_strip("C:/Users/arnfi/Desktop/Coding/ovl/OVLs/anim test/rot_x_0_22_42_def_c_new_end.maniskeys", increment=5)


import math
import mathutils


def convert(vcol):
    FAC = 1.9
    r = (vcol[0] - 0.5) * FAC
    # green appears to be unused
    # g = (vcol[1] - 0.5) * FAC
    b = (vcol[2] - 0.5) * FAC
    # alpha is used to control the shape of the strands, apparent softness or clumping
    try:
        # calculate third component for unit vector
        # cf https://docs.unity3d.com/Packages/com.unity.shadergraph@6.9/manual/Normal-Reconstruct-Z-Node.html
        squares = (r * r) - (b * b)
        z = math.sqrt(1.0 - max(0.0, min(1.0, squares)))
    except:
        z = 0
    # this is the raw vector, in tangent space
    # this is like uv, so we negate the second component
    vec = mathutils.Vector((r, -b, z))
    r = (vcol[0] - 0.5) * 90
    # green appears to be unused
    # g = (vcol[1] - 0.5) * FAC
    b = (vcol[2] - 0.5) * 90
    rot = mathutils.Euler((math.radians(b), math.radians(r), 0))
    vec2 = mathutils.Vector((0.0, 0.0, 1.0))
    vec2.rotate(rot)
    print(vec, vec2)

print("start")
vcols = [(0.5, 0, 0.5, 1), (0.5, 0, 0.4, 1), (0.6, 0, 0.4, 1), (0.4, 0, 0.5, 1), (0.6, 0, 0.6, 1)]
for vcol in vcols:
    convert(vcol)
