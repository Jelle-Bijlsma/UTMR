from PyQt5 import QtCore, QtWidgets
from pydicom import dcmread
import matplotlib.pyplot as plt

# here live all the additional classes I'm using


class PopupInput(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

    def showdialog(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'input dialog', 'Is this ok?')
        if ok:
            return text
        else:
            return False


class PopupWaring(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("not that word")
        QtWidgets.QPushButton("a button")

    def showme(self):
        self.show()


# this should provide multithreading options for the dicom2png
class Worker1(QtCore.QObject):

    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def dicom2png(self, filelist, path, project_name):
        print(filelist)
        print(path)
        print(project_name)
        a = 0
        for element in filelist:
            a = a + 1
            # disregard non-dicom files
            if element[0:3] != 'IM_':
                continue

            # read file and put it in a use-able array
            string = path + element
            dicom = dcmread(string)
            array = dicom.pixel_array
            plt.imshow(array, cmap="gray")
            savestring = "./data/png/" + project_name + "/" + element + ".png"
            plt.savefig(savestring)
            self.progress.emit(a)
        self.finished.emit()

        return
