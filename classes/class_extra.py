import os

import cv2
import matplotlib.pyplot as plt
from PyQt5 import QtCore
from pydicom import dcmread

"""
here live all the additional  small classes I'm using
"""


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
        # print("we here")
        for element in filelist:
            self.a = self.a + 1
            print("also here?")
            # disregard non-dicom files
            # if element[0:3] != 'IM_':
            #     print("incorrect filestring")
            #     continue
            # else:
            #     print("not")
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
        # print("and here")
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


def labwrap(key, m_fun, inner_fun):
    """"
    function wraps for _coolfun
    """
    return lambda: m_fun(key, inner_fun)


def labwrap3(mylist, element, textget):
    """"
    function wraps for setting the line_edits when manually entered
    """
    return lambda: mylist[element].setValue(int(textget()))


class SliderClass:
    all_sliders = []

    def __init__(self, slides, line_edits, function, keyword, radio, checklist=None):
        self.__class__.all_sliders.append(self)

        if checklist is None:
            checklist = []
        # the lists contain all the sliders, lineEdits and checkboxes used for a specific group.
        self.sliderlist = slides
        self.line_editlist = line_edits
        self.checklist = checklist
        self.keyword = keyword
        # _coolfun collects the data from the sliders and checkboxes and sends them to the movieclass
        self._coolfun = labwrap(keyword, function, self.getvalue)
        self._coolfun()  # call it to initialize all the line_edits.

        for slider in self.sliderlist:
            slider.valueChanged.connect(self._coolfun)
        for checkbox in self.checklist:
            checkbox.clicked.connect(self._coolfun)

        tracker = 0
        for line_edit in line_edits:
            line_edit.returnPressed.connect(labwrap3(self.sliderlist, tracker, line_edit.text))
            tracker += 1

    def value_set(self, value, number):
        # sets the value of the slider to a specific value. Currently only used when resetting the sliders.
        # could later be used to load in parameters from a previously saved session for example.
        self.sliderlist[number].setValue(value)

    def value_reset(self, value):
        # sets the value of the slider to a specific value. Currently only used when resetting the sliders.
        # could later be used to load in parameters from a previously saved session for example.
        for element in self.sliderlist:
            element.setValue(value)
        for element in self.checklist:
            if value == 0:
                element.setChecked(0)

    def woof(self):
        print(self.keyword)
        print("woof")

    def getvalue(self) -> list:
        """
        :rtype: list containing the values of each slider.
        """
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

        return vallist
