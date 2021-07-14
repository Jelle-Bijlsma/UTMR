import numpy as np

import functions.auxiliary
from functions.auxiliary import change_qpix as cqpx
from functions.auxiliary import calc_fft as cfft

class FrameClass:
    def __init__(self, frame: np.array):
        # frames are np.arrays used for different purposes. Bundled in a dictionary for easy acces. Name and key given:
        # original  : original immutable frame, made during __init__
        # gls       : gray level slicing image. What comes after the initial sliders.
        # bfilter   : buttersworth frequency domain filter

        # qpix are 'images' in the right format to be set to QLabels. The following qpix exist:
        # main      : the 'main' image shown in the videoplayer
        # fft       : the fourier transform of main
        # bfilter   : the buttersworth filter (in frequency domain)

        self.frames = {'original': frame, 'gls': frame}
        self.qpix = {'main': cqpx(frame), 'fft': cfft(frame, qpix=True)}
        self.histogram = functions.auxiliary.calc_hist(self.frames['original'])

        self.parameters = {'gls': [0, 0, 0, 0]}
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
        self.frames['gls'] = self.frames['gls'].astype(np.int16, casting='unsafe')
        temp = np.where((self.frames['gls'] >= lbound) & (self.frames['gls'] <= rbound), self.frames['gls'] + boost,
                        self.frames['gls'])
        temp = np.where(temp > 255, 255, temp)
        pre_gls = np.where(temp < 0, 0, temp)

        self.frames['gls'] = pre_gls.astype('uint8')
        self.qpix['main'] = cqpx(self.frames['gls'])
        self.parameters['gls'] = new_slice_p
        print("gls calc")

    def return_info(self, gls_p):
        if gls_p != self.parameters['gls']:
            self.calc_gls(gls_p)
            self.qpix['fft'] = cfft(self.frames['gls'], qpix=True)
        else:
            print("nothing")
        self.histogram = functions.auxiliary.calc_hist(self.frames['gls'])

    #
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
