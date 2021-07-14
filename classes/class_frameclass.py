import numpy as np
from PyQt5 import QtGui


class FrameClass:
    def __init__(self, frame: np.array):
        self.ogframe = frame  # original and immutable (for reference)
        self.grayframe = frame  # mutable
        self.gls = frame  # sliced grayscale
        self.qpix = self.change_qpix(self.ogframe)
        self.fft = self.change_qpix(self.ogframe)  # stop pycharm from whining but doesnt make sense otherwise
        # Qpix will be sent out to the label for display
        self.brightness = 0
        self.histogram = None
        self.has_valid_histogram = False
        self.has_valid_fft = False
        self.gray_slice_p = [0, 0, 0, 0]
        # brightness[0] boost[1]  lbound[2]  rbound[3]
        self.filter_b = np.empty(0)
        self.b_filter_p = [False, 0, 0]

    def change_qpix(self, frame):
        w, h = frame.shape
        qim = QtGui.QImage(frame.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
        return QtGui.QPixmap.fromImage(qim)

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
        self.has_valid_fft = False
        self.qpix = self.change_qpix(self.gls)
        # print("gls_calced")

    def calc_hist(self):
        l, b = self.gls.shape
        img2 = np.reshape(self.gls, l * b)
        # taking the log due to the huge difference between the amount of completely black pixels and the rest
        # adding + 1 else taking the log is undefined (10log1) = ??
        self.histogram = np.log10(np.bincount(img2, minlength=255) + 1)
        # min length else you will get sizing errors.
        self.has_valid_histogram = True
        # print("hist_calced")

    def calc_fft(self):
        # https://docs.opencv.org/4.5.2/de/dbc/tutorial_py_fourier_transform.html
        self.ogFFT2 = np.fft.fft2(self.gls)
        if self.isfiltered is False:
            self.ogFFT = np.fft.fft2(self.gls)
        else:
            self.ogFFT = self.filtered_fft
        # outputs a float
        temp = np.fft.fftshift(self.ogFFT)
        temp = 20 * np.log(np.abs(temp))
        # rescale else the casting to .uint8 loops back and you get a black spot in the middle of the FFT
        temp *= 255/np.max(temp)
        temp = temp.astype(np.uint8)
        # have to cast to .uint8 or change_qpix messes up
        self.fft = self.change_qpix(temp)
        self.has_valid_fft = True
        # print("fft_calced")

    def calc_bfilter(self, filter,filterparams):
        if np.array_equal(filter,self.filter_b):
            return
        # Z = np.fft.ifftshift(Z)
        output = np.multiply(np.fft.fftshift(filter), self.ogFFT2)
        self.filtered_fft = output
        output = np.fft.ifft2(output)
        output *= 255 / np.max(output)
        output = output.astype(np.uint8)
        # self.gls = output
        self.qpix = self.change_qpix(output)
        self.filter_b = filter
        self.b_filter_p[1:2] = filterparams
        self.has_valid_fft = False
        self.isfiltered = True

