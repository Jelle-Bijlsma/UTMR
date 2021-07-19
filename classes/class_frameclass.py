import cv2
import numpy as np

import functions.auxiliary
import functions.image_process
from functions.image_process import change_qpix as cqpx
from functions.image_process import calc_fft as cfft
from functions.image_process import float_uint8 as flui8

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

        self.histogram = functions.image_process.calc_hist(self.frames['original'])

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
            self.histogram = functions.image_process.calc_hist(self.frames['gls'])
            self.isvalid['histogram'] = True

    def calc_bfilter(self, b_filter):
        # filters come in the undeformed state, thus to properly multiply them, they have to be shifted
        self.fft_frames['b_filter_a'] = np.multiply(self.fft_frames['gls'], np.fft.fftshift(b_filter))
        after_b_filter = np.fft.ifft2(self.fft_frames['b_filter_a'])
        # this is a FFT, which is shifted. dtype = float
        self.isvalid['histogram'] = False
        self.qpix['main'] = cqpx(after_b_filter)
        self.qpix['fft'] = cqpx(functions.image_process.prep_fft(self.fft_frames['b_filter_a']))

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
        self.qpix['fft'] = cqpx(functions.image_process.prep_fft(self.fft_frames['g_filter_a']))

    #def calc_sobel(self):
     #   cv2.Sobel(src=

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
