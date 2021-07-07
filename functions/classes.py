import numpy as np
from PyQt5 import QtCore, QtGui
from pydicom import dcmread
import matplotlib.pyplot as plt
import os
import cv2
import matplotlib

matplotlib.use("Qt5Agg")

# here live all the additional classes I'm using


class Workersignals(QtCore.QObject):
    # This could be redundant due to an error I made previously.
    # Could incorporate in the Worker1?
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
        size = (0, 0)  # initialize to stop pycharm from whining
        # check if list is nonempty
        if filelist:
            for element in filelist:
                # print(element)
                fp = path + element
                img = cv2.imread(fp)
                h, w, trash = img.shape
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


class FrameClass:
    def __init__(self, frame: np.array):
        self.ogframe = frame  # original and immutable (for reference)
        self.newframe = frame  # mutable
        # qpix will be sent out to the label for display
        self.qpix = 0  # not an int! stop pycharm from whining
        self.change_qpix(self.ogframe)

        self.brightness = 0
        self.histogram = None
        self.has_valid_histogram = False
        self.gray_slice_p = [0, 0, 0]

    def change_qpix(self, frame):
        w, h = frame.shape
        qim = QtGui.QImage(frame.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
        self.qpix = QtGui.QPixmap.fromImage(qim)

    def change_brightness(self, bval):
        self.brightness = bval
        bval = int(bval)  # cast to be sure

        if bval > 0:
            self.newframe = np.where((255 - self.ogframe) < bval, 255, self.ogframe + bval)
        else:
            self.newframe = np.where((self.ogframe + bval) < 0, 0, self.ogframe + bval)
            self.newframe = self.newframe.astype('uint8')

        self.has_valid_histogram = False
        self.change_qpix(self.newframe)

   # def change_grayslicep(self,frame,newparams: list):


    def calc_hist(self):
        l, b = self.newframe.shape
        img2 = np.reshape(self.newframe, l * b)
        # taking the log due to the huge difference between the amount of completely black pixels and the rest
        # adding + 1 else taking the log is undefined (10log1) = ??
        self.histogram = np.log10(np.bincount(img2, minlength=255)+1)
        # min length else you will get sizing errors.
        self.has_valid_histogram = True


class MovieClass:
    def __init__(self):
        self.currentframe = 0
        self.maxframes = 0
        self.framelist = []
        self.brightness = 0
        self.gray_slice_p = [0, 0, 0]

    def create_frameclass(self, imlist):
        self.framelist.clear()
        for element in imlist:
            self.framelist.append(FrameClass(element))
        self.maxframes = len(imlist)-1

    def next_frame(self):
        if self.currentframe == self.maxframes:
            self.currentframe = 0
        else:
            self.currentframe += 1

    def return_frame(self):
        # temp is a reference to the object in the list, so modifications to temp are propageted
        # meaning, after all the frames have been adjusted, no more calculations are done.
        temp = self.framelist[self.currentframe]
        if self.brightness != temp.brightness:
            temp.change_brightness(self.brightness)
        if temp.has_valid_histogram is False:
            temp.calc_hist()
        return temp.qpix, temp.histogram

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
