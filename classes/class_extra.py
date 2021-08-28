import copy
import os

import cv2
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtWidgets
from pydicom import dcmread

"""
here live all the additional  small classes I'm using
"""


class QtDesignError(Exception):
    pass


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
    function wraps for _coolfun, i.e. editing the dictionary in 'MovieUpdate' class
    """
    return lambda: m_fun(key, inner_fun)


def labwrap3(mylist, element, textget):
    """"
    function wraps for setting the line_edits when manually entered
    """
    return lambda: mylist[element].setValue(int(textget()))


def special_print(text, value):
    if value is True:
        print(text)
    else:
        pass


class SliderClass:
    all_sliders = []

    def __init__(self, slides, line_edits, function, keyword, radiotuple=None, checklist=None):
        self.__class__.all_sliders.append(self)
        """"
        :slides:            sliderlist
        :line_edits:        line_edit list
        :function           current movie dict change
        :keyword            keyword for in the dictionary
        :radiotuple         if you do the setting twice
        :checklist          list of all checkboxes
        """

        # the lists contain all the sliders, lineEdits and checkboxes used for a specific group.
        self.sliderlist = slides
        self.line_editlist = line_edits
        self.checklist = checklist
        self.keyword = [keyword]
        self.expose_path = False  # print statement
        self._params_image = []  # this gets filled in during the first run of ._coolfun

        # same concept for the checklist, if no list is provided we take an empty list.
        if self.checklist is None:
            self.checklist = []

        # For the case of, for example, 'circlefind', there is no need for a radiotuple, since it is only applied
        # once. Thus, if it is not required, we will not set it.
        if radiotuple is not None:
            self.radio_image, self.radio_circle = radiotuple
            self.radio_image.clicked.connect(lambda: self.goto_radio("image"))
            self.radio_circle.clicked.connect(lambda: self.goto_radio("circle"))
        else:
            self.radio_image = None

        # _coolfun collects the data from the sliders and checkboxes and sends them to the movieclass
        self._coolfun = labwrap(self.keyword, function, self.getvalue)
        # _coolfun = curmov.valuechanged(keyword,self.getvalue)
        self._coolfun()  # call it to initialize all the line_edits.
        # had to do it twice, else the calls dont check out

        for slider in self.sliderlist:
            slider.valueChanged.connect(self._coolfun)
        for checkbox in self.checklist:
            # remember checkboxes take the .stateChanged signal not pressed/clicked or whatever
            checkbox.stateChanged.connect(self._coolfun)

        if radiotuple is not None:
            self._params_circle = copy.copy(self._params_image)

        tracker = 0
        for line_edit in line_edits:
            line_edit.returnPressed.connect(labwrap3(self.sliderlist, tracker, line_edit.text))
            tracker += 1

    def goto_radio(self, strz):
        """"
        Remember to define the list upfront, since when you start changing values, signals will be sent to '_cool_fun'
        and thus the 'self._params...' gets updated immediatley. Set 'expose_path' to True in  to see the effect.
        """
        if strz == "image":
            thelist = self._params_image
        elif strz == "circle":
            thelist = self._params_circle
        else:
            raise Exception(f"you managed to call 'goto_radio' with {strz}??")

        self.settr(thelist)

    def settr(self, thelist):
        combolist = self.checklist + self.sliderlist
        # print(f" this is the combolist {combolist}")
        self.getvalue()  # a little bit hacky trick to get the keyvalue to update properly.
        for element, iterator in zip(combolist, range(len(combolist))):
            if isinstance(element, QtWidgets.QCheckBox):
                element.setChecked(thelist[iterator])
                continue
            special_print(f"changed one element:\nthelist = {thelist}", self.expose_path)
            element.setValue(thelist[iterator])

    def value_reset(self, value):
        # sets the value of the slider to a specific value. Currently only used when resetting the sliders.
        # could later be used to load in parameters from a previously saved session for example.
        for element in self.sliderlist:
            element.setValue(value)
        for element in self.checklist:
            if value == 0:
                element.setChecked(0)

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

        if self.radio_image is not None:
            if self.radio_image.isChecked():
                self._params_image = vallist
                special_print("Edited the image parameters", self.expose_path)
                if len(self.keyword) == 2:
                    self.keyword.pop()
                else:
                    pass
            elif self.radio_circle.isChecked():
                self._params_circle = vallist
                special_print("Edited the circle parameters", self.expose_path)
                if len(self.keyword) == 1:
                    self.keyword.append("2")
                else:
                    pass
            else:
                raise QtDesignError("None of the radiobuttons are pressed! \n at least one of the two should be pressed"
                                    "at all times.")
        else:
            self._params_image = vallist

        return vallist
