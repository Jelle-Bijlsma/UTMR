import cv2
import numpy as np

import functions.auxiliary
import functions.image_processing.image_process
from functions.image_processing.image_process import change_qpix as cqpx
from functions.image_processing.image_process import calc_fft as cfft
import copy
from PyQt5 import QtGui

class FrameClass:
    def __init__(self, frame: np.array):
        # initialization for FrameClass method.

        self.frames = {'original': frame, 'gls': frame, 'b_filter_a': frame}
        # frames are np.arrays used for different purposes. Bundled in a dictionary for easy acces.
        # They are of dimension frame.shape() and are "dtype='uint8'"
        # Name and key given:
        # original  : original immutable frame, made during __init__
        # gls       : gray level slicing image. What comes after the initial sliders.

        self.qpix = {'main': cqpx(frame), 'fft': cfft(frame, qpix=True)}
        # qpix are 'images' in the right format to be set to QLabels. The following qpix exist:
        # main      : the 'main' image shown in the videoplayer
        # fft       : the fourier transform of main

        self.fft_frames = {'main': cfft(frame), 'gls': cfft(frame), 'b_filter_a': cfft(frame),
                           'g_filter_a': cfft(frame)}
        # fft_frames are similar to frames except for the fact that they are NOT 'uint8'. Convention to have them
        # NOT centered aesthetically.
        # main:      : the fft of the frame
        # gls        : fft of the gls
        # b_filter_a : fft of gls after filtering with b_filter

        self.histogram = functions.image_processing.image_process.calc_hist(self.frames['original'])

        self.isvalid = {'histogram': False, 'b_filter': False, 'g_filter': False}

        self.parameters = {'gls': [0, 0, 0, 0], 'shape': frame.shape}
        # the parameters can be explained as follows
        # gls: brightness[0] boost[1]  lbound[2]  rbound[3]

    def calc_gls(self, new_slice_p: list):
        # gls has two main functions. Brightness (#B) adjustment and Graylevel slicing.
        # easy reading by pulling the new slice parameters apart.
        bval = new_slice_p[0]
        boost = new_slice_p[1]
        lbound = new_slice_p[2]
        rbound = new_slice_p[3]

        if bval > 0:  # B
            self.frames['gls'] = np.where((255 - self.frames['original']) < bval, 255, self.frames['original'] + bval)
        else:
            self.frames['gls'] = np.where((self.frames['original'] + bval) < 0, 0, self.frames['original'] + bval)
        # gls
        self.frames['gls'] = self.frames['gls'].astype(np.int16)
        temp = np.where((self.frames['gls'] >= lbound) & (self.frames['gls'] <= rbound), self.frames['gls'] + boost,
                        self.frames['gls'])
        temp = np.where(temp > 255, 255, temp)
        pre_gls = np.where(temp < 0, 0, temp)

        self.frames['gls'] = pre_gls.astype('uint8')
        self.qpix['main'] = cqpx(self.frames['gls'])
        self.fft_frames['gls'] = cfft(self.frames['gls'])

        self.parameters['gls'] = new_slice_p
        self.isvalid['histogram'] = False  # after gls we need to recalculate the histogram.
        print("gls calc")

    def return_info(self, gls_p, bool_b_filter, b_filter, bool_g_filter, g_filter):
        # always do a gls check first. It is the base on which the rest runs.
        self.calc_gls(gls_p)
        self.isvalid['b_filter'] = bool_b_filter
        self.isvalid['g_filter'] = bool_g_filter
        if bool_b_filter is True:
            self.calc_bfilter(b_filter)
        if bool_g_filter is True:
            self.calc_gfilter(g_filter)
        if (bool_g_filter is False) & (bool_b_filter is False):
            self.qpix['fft'] = cfft(self.frames['gls'], qpix=True)

        if self.isvalid['histogram'] is False:
            # since histogram has no inherent parameters we do a check against a manual one to avoid over-calculation.
            self.histogram = functions.image_processing.image_process.calc_hist(self.frames['gls'])
            self.isvalid['histogram'] = True

    def calc_bfilter(self, b_filter):
        # filters come in the undeformed state, thus to properly multiply them, they have to be shifted
        self.fft_frames['b_filter_a'] = np.multiply(self.fft_frames['gls'], np.fft.fftshift(b_filter))
        after_b_filter = np.fft.ifft2(self.fft_frames['b_filter_a'])
        # this is a FFT, which is shifted. dtype = float
        self.isvalid['histogram'] = False
        self.qpix['main'] = cqpx(after_b_filter)
        self.qpix['fft'] = cqpx(functions.image_processing.image_process.prep_fft(self.fft_frames['b_filter_a']))

    def calc_gfilter(self, g_filter):
        if self.isvalid['b_filter']:
            prev_frame = self.fft_frames['b_filter_a']
        else:
            prev_frame = self.fft_frames['gls']
        self.fft_frames['g_filter_a'] = np.multiply(prev_frame, np.fft.fftshift(g_filter))
        after_g_filter = np.fft.ifft2(self.fft_frames['g_filter_a'])
        # this is a FFT, which is shifted. dtype = float
        self.isvalid['histogram'] = False
        self.qpix['main'] = cqpx(after_g_filter)
        self.qpix['fft'] = cqpx(functions.image_processing.image_process.prep_fft(self.fft_frames['g_filter_a']))

    def calc_sobel(self):
        # https://stackoverflow.com/questions/37552924/convert-qpixmap-to-numpy
        # https://stackoverflow.com/questions/45020672/convert-pyqt5-qpixmap-to-numpy-ndarray

        original_image = cv2.imread("./data/png/correct_video/IM_0011.png", 0)
        print(original_image.dtype)
        w,h = np.shape(original_image)
        Qimage = QtGui.QImage(original_image.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
        QPix_OG = QtGui.QPixmap.fromImage(Qimage)
        print("we doin this")
        Qimage_return = QtGui.QPixmap.toImage(QPix_OG)
        # from here we try to make the array

        s = Qimage_return.bits()
        print(type(s))
        print(s)
        s = s.asstring(w*h)
        print(type(s))
        new_array = np.fromstring(s, dtype=np.uint8).reshape((h,w))

        new_array = self.qt_image_to_array(Qimage)
        # print(np.array_equal(new_array,original_image))

        # now that we have the array we can convert it back again
        Qimage2 = QtGui.QImage(new_array.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
        QPix_2 = QtGui.QPixmap.fromImage(Qimage2)
        #sameqpix = QtGui.QPixmap.toImage(QPix_2)
        # sameqpix = cqpx(return_image)
        return QPix_2, QPix_OG

    def qt_image_to_array(self, img: QtGui.QImage, share_memory=False):
        """ Creates a numpy array from a QImage.

            If share_memory is True, the numpy array and the QImage is shared.
            Be careful: make sure the numpy array is destroyed before the image,
            otherwise the array will point to unreserved memory!!
        """
        assert isinstance(img, QtGui.QImage), "img must be a QtGui.QImage object"
        assert img.format() == QtGui.QImage.Format_Indexed8, \
            "img format must be QImage.Format.Format_RGB32, got: {}".format(img.format())

        img_size = img.size()
        buffer = img.constBits()  # Returns a pointer to the first pixel data.
        buffer.setsize(img_size.height()*img_size.width()*8) # the 8 might be 4 if youre not running 64bit
        # https://stackoverflow.com/questions/3853312/sizeof-void-pointer (OR is it for uint8?)
        # https://doc.qt.io/qt-5/qimage.html#constBits

        # Sanity check
        n_bits_buffer = len(buffer)
        n_bits_image = img_size.width() * img_size.height() * img.depth()
        assert n_bits_buffer == n_bits_image, \
            "size mismatch: {} != {}".format(n_bits_buffer, n_bits_image)

        assert img.depth() == 8, "unexpected image depth: {}".format(img.depth())

        # Note the different width height parameter order!
        arr = np.ndarray(shape=(img_size.height(), img_size.width(), img.depth()//8),
                         buffer=buffer,
                         dtype=np.uint8)

        if share_memory:
            return arr
        else:
            return copy.deepcopy(arr)

    # def calc_bfilter(self, filter, filterparams):
    #     if np.array_equal(filter, self.filter_b):
    #         return
    #     # Z = np.fft.ifftshift(Z)
    #     output = np.multiply(np.fft.fftshift(filter), self.ogFFT2)
    #     self.filtered_fft = output
    #     output = np.fft.ifft2(output)
    #     output *= 255 / np.max(output)
    #     output = output.astype(np.uint8)
    #     # self.gls = output
    #     self.qpix = cqpx(output)
    #     self.filter_b = filter
    #     self.b_filter_p[1:2] = filterparams
    #     self.has_valid_fft = False
    #     self.isfiltered = True
