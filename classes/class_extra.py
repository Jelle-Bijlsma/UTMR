import os
import cv2
import matplotlib.pyplot as plt
from PyQt5 import QtCore
from pydicom import dcmread


# here live all the additional  small classes I'm using
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


class SliderClass:
    def __init__(self, slides, line_edits, function, checklist=None):
        # Usecase of thsi class. Many specific sliders, lineEdits and checkboxes are used together. Instead of
        # 'hard-coding' all these things, using the SliderClass Class gives some ease of programming

        # Order of 'slides' is important. Could maybe improve this?
        if checklist is None:
            checklist = []
        # the lists contain all the sliders, lineEdits and checkboxes used for a specific group.
        self.sliderlist = slides
        self.line_editlist = line_edits
        self.checklist = checklist
        # .setfun takes a function as argument and connects the valueChanged signal to it for every element
        # in the sliderlist and the clicked.connect to every element in the checklist.
        self.setfun(function)

    def valueset(self, value):
        # sets the value of the slider to a specific value. Currently only used when resetting the sliders.
        # could later be used to load in parameters from a previously saved session for example.
        for element in self.sliderlist:
            element.setValue(value)
        for element in self.checklist:
            if value == 0:
                element.setChecked(0)

    def getvalue(self):
        vallist = []
        # go over the checkboxes, putting False for 0 and True for 1
        for element in self.checklist:
            stateval = element.checkState()
            if stateval == 0:
                vallist.append(False)
            else:
                vallist.append(True)
        # simultaneously add slidervalue to list and update the line-edits
        for slider, lineedit in zip(self.sliderlist, self.line_editlist):
            slidervalue = slider.value()
            vallist.append(slidervalue)
            lineedit.setText(str(slidervalue))
        print(vallist)
        return vallist

    def setfun(self, function):
        for element in self.sliderlist:
            element.valueChanged.connect(function)
        for element in self.checklist:
            element.clicked.connect(function)

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
