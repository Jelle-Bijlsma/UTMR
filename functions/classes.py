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
        self.ogframe = frame    # original and immutable (for reference)
        self.grayframe = frame  # mutable
        self.gls = frame        # sliced grayscale
        # Qpix will be sent out to the label for display
        self.qpix = 0  # not an int! stop pycharm from whining
        self.change_qpix(self.ogframe)

        self.brightness = 0
        self.histogram = None
        self.has_valid_histogram = False
        self.gray_slice_p = [0,         0,         0,       0]
        #               brightness[0] boost[1]  lbound[2]  rbound[3]

    def change_qpix(self, frame):
        w, h = frame.shape
        qim = QtGui.QImage(frame.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
        self.qpix = QtGui.QPixmap.fromImage(qim)

    def change_grayslicep(self, new_slice_p: list):
        if self.gray_slice_p[0] != new_slice_p[0]:
            bval = int(new_slice_p[0])  # cast to be sure
            if bval > 0:
                self.grayframe = np.where((255 - self.ogframe) < bval, 255, self.ogframe + bval)
            else:
                self.grayframe = np.where((self.ogframe + bval) < 0, 0, self.ogframe + bval)
                self.grayframe = self.grayframe.astype('uint8')

        if self.gray_slice_p[0:4] != new_slice_p[0:4]:
            # print(new_slice_p)
            boost = new_slice_p[1]
            lbound = new_slice_p[2]
            rbound = new_slice_p[3]
            self.grayframe = self.grayframe.astype(np.int16, casting='unsafe')
            # print(self.grayframe.dtype)
            temp = np.where((self.grayframe >= lbound) & (self.grayframe <= rbound), self.grayframe + boost,
                            self.grayframe)
            temp2 = np.where(temp > 255, 255, temp)
            temp2 = np.where(temp2 < 0, 0, temp2)
            self.gls = temp2.astype(np.uint8)
            self.grayframe = self.grayframe.astype(np.uint8)

        self.gray_slice_p = new_slice_p
        self.has_valid_histogram = False
        self.change_qpix(self.gls)

    def calc_hist(self):
        l, b = self.gls.shape
        img2 = np.reshape(self.gls, l * b)
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
        self.gray_slice_p = [0, 0, 0, 0]

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
        # compare expected values (of movieclass) to frameclass
        if self.gray_slice_p != temp.gray_slice_p:
            temp.change_grayslicep(self.gray_slice_p)
        if temp.has_valid_histogram is False:
            temp.calc_hist()
        return temp.qpix, temp.histogram


class SliderClass:
    def __init__(self, slides, line_edits):
        # Order of 'slides' is important for use is the initial brightness section. Could maybe improve this
        # by using key value pairs?
        self.sliderlist = slides
        self.line_editlist = line_edits

    def valueset(self, value):
        for element in self.sliderlist:
            element.setValue(value)

    def getvalue(self):
        vallist = []
        for slider, lineedit in zip(self.sliderlist, self.line_editlist):
            slidervalue = slider.value()
            vallist.append(slidervalue)
            lineedit.setText(str(slidervalue))
        return vallist

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
