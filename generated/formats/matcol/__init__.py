from generated.formats.matcol.compound.MaterialcollectionInfoHeader import MaterialcollectionInfoHeader
from generated.io import IoFile


class MatcolFile(MaterialcollectionInfoHeader, IoFile):

    def __init__(self,):
        super().__init__()

    def load(self, filepath, commands=(), mute=False):
        eof = super().load(filepath)


if __name__ == "__main__":
    m = MatcolFile()
    m.load("C:/Users/arnfi/Desktop/carch/carcharodontosaurus.matcol")
    print(m)