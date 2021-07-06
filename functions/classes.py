import numpy as np
from PyQt5 import QtCore, QtWidgets
from pydicom import dcmread
import matplotlib.pyplot as plt
import os
import cv2
# import auxillary

# here live all the additional classes I'm using


# class PopupInput(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#
#     def showdialog(self):
#         text, ok = QtWidgets.QInputDialog.getText(self, 'input dialog', 'Is this ok?')
#         if ok:
#             return text
#         else:
#             return False
#
#
# class PopupWaring(QtWidgets.QDialog):
#     def __init__(self,text):
#         super().__init__()
#         self.setWindowTitle("watch out kid")
#         a = QtWidgets.QLabel()
#         a.setText("this thing aint on autopilot son ")
#         QtWidgets.QPushButton("a button")
#
#     def showme(self):
#         self.show()


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


# class FrameClass:
#     def __init__(self, frame: np.array):
#         self.ogframe = frame  # original and immutable
#         self.qpix = auxillary.cv2qpix(self.ogframe)
#         self.brightness = 0
#         self.newframe = frame
#
#     def change_qpix(self, frame):
#         # this is weird, import function soon?
#         self.qpix = auxillary.cv2qpix(frame)
#
#     def change_brightness(self, bval):
#         self.brightness = bval
#         bval = int(bval)  # cast to be sure
#
#         if bval > 0:
#             self.newframe = np.where((255 - self.ogframe) < bval, 255, self.ogframe + bval)
#         else:
#             self.newframe = np.where((self.ogframe + bval) < 0, 0, self.ogframe + bval)
#             self.newframe = self.newframe.astype('uint8')
#
#         self.change_qpix(self.newframe)
#
#
# class MovieClass:
#     def __init__(self):
#         self.currentframe = 0
#         self.maxframes = 0
#
#     def create_frameclass(self,imlist):
#
#
#     def next_frame(self):
#         if self.currentframe == self.maxframes:
#             self.currentframe = 0
#         else:
#             self.currentframe += 1
