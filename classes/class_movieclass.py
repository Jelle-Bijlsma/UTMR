import numpy as np
from PyQt5 import QtGui
import functions.auxiliary
import class_frameclass


class MovieClass:
    def __init__(self):
        self.currentframe = 0
        self.maxframes = 0
        self.framelist = []
        self.brightness = 0
        self.gray_slice_p = [0, 0, 0, 0]
        # brightness[0] boost[1]  lbound[2]  rbound[3]
        self.b_filter_p = [False, 1, 0]
        # on [0] cutoff [1] order [2]
        self.b_filter = np.empty(0)
        self.b_filter_out = np.empty(1, 1)

    def create_frameclass(self, imlist):
        self.framelist.clear()
        for element in imlist:
            self.framelist.append(class_frameclass.FrameClass(element))
        self.maxframes = len(imlist) - 1

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
        if temp.has_valid_fft is False:
            temp.isfiltered = False
            temp.calc_fft()
            if not self.b_filter.any():
                self.b_filter = temp.ogFFT  # just a placeholder for the size
                self.getnewbfilter()
        if self.b_filter_p[0] is True:
            if self.b_filter_p[1:2] != temp.b_filter_p[1:2]:
                temp.calc_bfilter(self.b_filter, self.b_filter_p[1:2])
                temp.calc_fft()
        return temp.qpix, temp.histogram, temp.fft, self.b_filter_out
        # movieclass keeps the b_filter

    def getnewbfilter(self):
        self.b_filter = functions.auxiliary.butter_filter(self.b_filter, self.b_filter_p[1], self.b_filter_p[2])
        self.b_filter_out = self.b_filter
        self.b_filter_out *= 255 / np.max(self.b_filter)
        self.b_filter_out = self.b_filter_out.astype(np.uint8)
        w, h = self.b_filter.shape
        qim = QtGui.QImage(self.b_filter_out.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
        self.b_filter_out = QtGui.QPixmap.fromImage(qim)
