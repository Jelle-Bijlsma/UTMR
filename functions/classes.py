from PyQt5 import QtCore, QtWidgets
from pydicom import dcmread
import matplotlib.pyplot as plt
import os
import cv2


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


class Workersignals(QtCore.QObject):
    starting = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)
    videodone = QtCore.pyqtSignal()


# this should provide multithreading options for the dicom2png
class Worker1(QtCore.QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = Workersignals()
        self.a = 0

    def dicom2png(self, filelist, path, project_name):
        self.signals.starting.emit()
        self.a = 0
        for element in filelist:
            self.a = self.a + 1
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
            self.signals.progress.emit(self.a)
            plt.close()
        self.signals.finished.emit()
        return

    def png2avi(self, path, fps, savename):
        # them ting be needing PNG
        filelist = os.listdir(path)
        filelist.sort()
        img_array = []
        print("u are here" + path)
        print(filelist)
        # check if list is nonempty
        # save location is still wrong!
        if filelist:
            for element in filelist:
                # print(element)
                fp = path + element
                img = cv2.imread(fp)
                h, w, l = img.shape
                # notice the reversal of order ...
                size = (w, h)
                img_array.append(img)

            out = cv2.VideoWriter(savename, cv2.VideoWriter_fourcc(*'FFV1'), fps, size)
            for i in range(len(img_array)):
                out.write(img_array[i])
            out.release()
        else:
            print(path + "was empty")
        # fourcc: Een FourCC is een reeks van vier bytes gebruikt om dataformaten te identificeren.
        self.signals.videodone.emit()
        return
