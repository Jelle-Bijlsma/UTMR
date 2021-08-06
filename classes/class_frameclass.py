import cv2
import numpy as np
from PyQt5 import QtGui
from scipy import interpolate


import functions.auxiliary
import functions.image_processing.image_process
from functions.image_processing.image_process import calc_fft as cfft
from functions.image_processing.image_process import change_qpix as cqpx


class FrameClass:
    def __init__(self, frame: np.array):
        # initialization for FrameClass method.

        self.frames = {'original': frame, 'gls': frame, 'b_filter_a': frame, 'g_filter_a': frame}
        """ frames are np.arrays used for different purposes. Bundled in a dictionary for easy acces.
        They are of dimension frame.shape() and are "dtype='uint8'"
        Name and key given:
        original  : original immutable frame, made during __init__
        gls       : gray level slicing image. What comes after the initial sliders."""

        self.qpix = {'main': cqpx(frame), 'fft': cfft(frame, qpix=True),
                     'empty': cqpx(np.zeros([100, 100], dtype='uint8'))}
        """ qpix are 'images' in the right format to be set to QLabels. The following qpix exist:
        ( i am afraid a bit more already exist, I havent kept up with them ) 
        main      : the 'main' image shown in the videoplayer
        fft       : the fourier transform of main
        empty     : returns a black screen"""

        self.fft_frames = {'main': cfft(frame), 'gls': cfft(frame), 'b_filter_a': cfft(frame),
                           'g_filter_a': cfft(frame)}
        # fft_frames are similar to frames except for the fact that they are NOT 'uint8'. Convention to have them
        # NOT centered aesthetically.
        # main:      : the fft of the frame
        # gls        : fft of the gls
        # b_filter_a : fft of gls after filtering with b_filter

        self.histogram = functions.image_processing.image_process.calc_hist(self.frames['original'])

        self.isvalid = {'histogram': False, 'b_filter': False, 'g_filter': False}
        self.valid_ops = ["dilate", "erosion", "m_grad", "blackhat", "whitehat"]
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
            self.frames['gls'] = np.where((255 - self.frames['original']) < bval, 255,
                                          self.frames['original'] + bval)
        else:
            self.frames['gls'] = np.where((self.frames['original'] + bval) < 0, 0, self.frames['original'] + bval)
        # gls
        self.frames['gls'] = self.frames['gls'].astype(np.int16)
        temp = np.where((self.frames['gls'] >= lbound) & (self.frames['gls'] <= rbound),
                        self.frames['gls'] + boost, self.frames['gls'])
        temp = np.where(temp > 255, 255, temp)
        pre_gls = np.where(temp < 0, 0, temp)

        self.frames['gls'] = pre_gls.astype('uint8')
        self.qpix['main'] = cqpx(self.frames['gls'])
        self.fft_frames['gls'] = cfft(self.frames['gls'])

        self.parameters['gls'] = new_slice_p
        self.isvalid['histogram'] = False  # after gls we need to recalculate the histogram.
        # print("gls calc")

    def calc_gls2(self, new_slice_p: list):
        # gls has two main functions. Brightness (#B) adjustment and Graylevel slicing.
        # easy reading by pulling the new slice parameters apart.
        bval = new_slice_p[0]
        boost = new_slice_p[1]
        lbound = new_slice_p[2]
        rbound = new_slice_p[3]

        if bval > 0:  # B
            self.frames['gls2'] = np.where((255 - self.frames['masked']) < bval, 255,
                                          self.frames['masked'] + bval)
        else:
            self.frames['gls2'] = np.where((self.frames['masked'] + bval) < 0, 0, self.frames['masked'] + bval)
        # gls
        self.frames['gls2'] = self.frames['gls2'].astype(np.int16)
        temp = np.where((self.frames['gls2'] >= lbound) & (self.frames['gls2'] <= rbound),
                        self.frames['gls2'] + boost, self.frames['gls2'])
        temp = np.where(temp > 255, 255, temp)
        pre_gls = np.where(temp < 0, 0, temp)

        self.frames['gls2'] = pre_gls.astype('uint8')
        self.qpix['main2'] = cqpx(self.frames['gls2'])
        self.fft_frames['gls2'] = cfft(self.frames['gls2'])

        return cqpx(self.frames['gls2'])

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
            # since histogram has no inherent parameters we do a check against a manual one to avoid
            # over-calculation.
            self.histogram = functions.image_processing.image_process.calc_hist(self.frames['gls'])
            self.isvalid['histogram'] = True

        self.isvalid['edge_base'] = False  # can the edge-finder rely on memory?

    def calc_bfilter(self, b_filter):
        # filters come in the undeformed state, thus to properly multiply them, they have to be shifted
        self.fft_frames['b_filter_a'] = np.multiply(self.fft_frames['gls'], np.fft.fftshift(b_filter))
        after_b_filter = np.fft.ifft2(self.fft_frames['b_filter_a'])
        # this is a FFT, which is shifted. dtype = float
        self.isvalid['histogram'] = False
        self.qpix['main'] = cqpx(after_b_filter)
        self.qpix['fft'] = cqpx(functions.image_processing.image_process.prep_fft(self.fft_frames['b_filter_a']))
        # add to the collection
        self.frames['b_filter_a'] = functions.image_processing.image_process.float_uint8(
            after_b_filter)

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
        self.frames['g_filter_a'] = functions.image_processing.image_process.float_uint8(
            after_g_filter)

    def calc_gfilter2(self, g_filter):
        # if self.isvalid['b_filter']:
        #     prev_frame = self.fft_frames['b_filter_a']
        # else:
        #     prev_frame = self.fft_frames['gls']
        self.fft_frames['g_filter_a2'] = np.multiply(self.fft_frames['gls2'], np.fft.fftshift(g_filter))
        after_g_filter = np.fft.ifft2(self.fft_frames['g_filter_a2'])
        # this is a FFT, which is shifted. dtype = float
        self.frames['g_filter_a2'] = functions.image_processing.image_process.float_uint8(
            after_g_filter)
        return cqpx(self.frames['g_filter_a2'])

    def call_edge(self, para_sobel, para_canny):
        """
        :arg para_sobel: A list containing all the parameters for Sobel Edge finding
        :arg para_canny: A list containing all the parameters for Canny Edge finding
        :rtype: (Qpix_main), Qpix_window)

        should draw text on screen both buttons can not be pressed together
        https://stackoverflow.com/questions/57017820/how-to-add-a-text-on-imagepython-gui-pyqt5
        """

        dosobel = para_sobel[0]
        docanny = para_canny[0]

        assert isinstance(dosobel, bool), "wrong paralist order sobel"
        assert isinstance(docanny, bool), "wrong paralist order canny"

        if self.isvalid['edge_base'] is False:
            Qimage = QtGui.QPixmap.toImage(self.qpix['main'])
            self.frames['pre_edge'] = functions.image_processing.image_process.qt_image_to_array(
                Qimage, share_memory=True)[:, :, 0]  # WHY is there data corruption if share memory is FALSE?!
            # take only the first 2d array because it returns a color channel while we work in grayscale.
            self.isvalid['edge_base'] = True
        elif self.isvalid['edge_base'] is True:
            pass

        print("here")
        if dosobel is True:
            returnable = self.calc_sobel(para_sobel[1:])
        elif docanny is True:
            returnable = self.calc_canny(para_canny[1:])
            print("there")
        else:
            # if neither are true, go to status quo.
            returnable = (self.qpix['main'], self.qpix['empty'])
            print("plsno")

        # later we add a median filter here
        return returnable

    def calc_canny(self, parameters: list):
        threshold1 = parameters[0]
        threshold2 = parameters[1]
        frame = self.frames['pre_edge']
        edges = cv2.Canny(frame, threshold1, threshold2)
        # print(f"canny shape is{np.shape(edges)}")

        # canny by default outputs 8bit.
        # https://docs.opencv.org/3.4/dd/d1a/group__imgproc__feature.html#ga04723e007ed888ddf11d9ba04e2232de
        self.frames['canny'] = edges
        return cqpx(edges), self.qpix['main']

    def canny2(self, parameters: list):
        threshold1 = parameters[0]
        threshold2 = parameters[1]
        frame = np.copy(self.frames['g_filter_a2'])
        edges = cv2.Canny(frame, threshold1, threshold2)
        # print(f"canny shape is{np.shape(edges)}")

        # canny by default outputs 8bit.
        # https://docs.opencv.org/3.4/dd/d1a/group__imgproc__feature.html#ga04723e007ed888ddf11d9ba04e2232de
        self.frames['canny2'] = edges
        return cqpx(self.frames['canny2'])

    def sobel2(self, parameters):
        frame = np.copy(self.frames['g_filter_a2'])
        ksize = parameters[0]
        scale = parameters[1]
        delta = parameters[2]

        grad_x = cv2.Sobel(frame, cv2.CV_16S, 1, 0, ksize=ksize, scale=scale, delta=delta,
                           borderType=cv2.BORDER_DEFAULT)
        grad_y = cv2.Sobel(frame, cv2.CV_16S, 0, 1, ksize=ksize, scale=scale, delta=delta,
                           borderType=cv2.BORDER_DEFAULT)

        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)
        grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
        # the gradient is shown in the main window, and in the third window we show the 'original' main
        # so no error but a bit ... ill conceived naming
        print(f"sobel shape is{np.shape(grad_x)}")

        self.frames['sobel2'] = functions.image_processing.image_process.float_uint8(grad)
        return cqpx(self.frames['sobel2'])

    def calc_sobel(self, parameters: list) -> (QtGui.QPixmap, QtGui.QPixmap):
        """
        :param parameters: [Ksize, Scale, Delta]
        :return: (Qpix_main, Qpix_window)
        """

        frame = self.frames['pre_edge']

        assert len(parameters) == 3, "Parameterlist length must be three"
        # assert all([isinstance(x, int) for x in params]) is True, "All parameters must be of type int"

        ksize = parameters[0]
        scale = parameters[1]
        delta = parameters[2]

        grad_x = cv2.Sobel(frame, cv2.CV_16S, 1, 0, ksize=ksize, scale=scale, delta=delta,
                           borderType=cv2.BORDER_DEFAULT)
        grad_y = cv2.Sobel(frame, cv2.CV_16S, 0, 1, ksize=ksize, scale=scale, delta=delta,
                           borderType=cv2.BORDER_DEFAULT)

        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)

        grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
        # the gradient is shown in the main window, and in the third window we show the 'original' main
        # so no error but a bit ... ill conceived naming
        print(f"sobel shape is{np.shape(grad_x)}")
        print(grad.dtype)
        self.frames['sobel'] = functions.image_processing.image_process.float_uint8(grad)
        print(self.frames['sobel'].dtype)
        return cqpx(grad), self.qpix['main']

    def domorph(self, textstring):
        if 'canny' in self.frames:
            self.frames['morph'] = np.copy(self.frames['canny'])
            cur_ele = self.frames['morph']
            for element in textstring.split('\n'):
                starter = element.split(' ')
                print(starter)
                kernelsize = (int(starter[2]), int(starter[2]))
                kernel = cv2.getStructuringElement(shape=int(starter[4]), ksize=kernelsize)
                if starter[0] == self.valid_ops[0]:  # dilate
                    cur_ele = cv2.dilate(cur_ele, kernel, iterations=1)
                elif starter[0] == self.valid_ops[1]:  # erosion
                    cur_ele = cv2.erode(cur_ele, kernel, iterations=1)
                elif starter[0] == self.valid_ops[2]:  # m_grad
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_GRADIENT, kernel)
                elif starter[0] == self.valid_ops[3]:  # blackhat
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_BLACKHAT, kernel)
                elif starter[0] == self.valid_ops[4]:  # whitehat
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_TOPHAT, kernel)
            self.frames['morph'] = cur_ele
            return cqpx(cur_ele)
        else:
            print("do canny first!")
            return None

    def call_flood(self,coords):
        x,y = coords
        if 'morph' in self.frames:
            before_fill = np.copy(self.frames['morph'])
            after_fill = np.copy(self.frames['morph'])
            h, w = self.frames['morph'].shape
            print(f"h:{h}, w:{w}")
            mask = np.zeros((h + 2, w + 2), np.uint8)
            cv2.floodFill(after_fill, mask, (x, y), 255)
            self.frames['mask'] = after_fill ^ before_fill
            self.frames['masked'] = self.frames['mask'] & self.frames['original']
            return cqpx(self.frames['mask']), cqpx(self.frames['masked'])
        else:
            print("no morph found?!")
            return

    def circlefind(self, parameters):
        if len(parameters) != 6:
            print(parameters)
            return cqpx(self.frames['original'])

        dp = parameters[0] / 25  # since PyQt does not allow for non int slider values, they have to be created.
        minDist = parameters[1]
        param1 = parameters[2]
        param2 = parameters[3]
        minradius = parameters[4]
        maxradius = parameters[5]

        imagepre = cv2.rotate(np.copy(self.frames['canny2']), cv2.ROTATE_90_CLOCKWISE)
        image = cv2.resize(imagepre,(900,900))
        # image = cv2.bitwise_not(image)

        circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist, param1=param1, param2=param2,
                                   minRadius=minradius, maxRadius=maxradius)

        if circles is not None:
            # since the hough detects the circles randomly, we have the need to sort them in ascending order
            # for the spline to work
            conlist = circles[0, :, 0:2]
            mysort = sorted(conlist, key=lambda p: p[0])
            mysort = np.array(mysort)
            x = mysort[:, 0]
            y = mysort[:, 1]
            # create spline
            spl = interpolate.InterpolatedUnivariateSpline(x, y, k=2)
            spl.set_smoothing_factor(0.5)
            # by creating a dense line grid to plot the spline over, we get smooth output
            xnew2 = np.linspace(np.min(x) - 20, np.max(x) + 20, num=60, endpoint=True)
            ynew2 = spl(xnew2)

            # this construction turns the separate xnew2 and ynew2 into an array of like this:
            # [[x0, y0]
            # [x1, y1]] etc..
            thelist = np.array([[x, y] for x, y in zip(xnew2, ynew2)], dtype="int")

            # we now want to round the list, to make them into accessible pixel values for plotting.
            # by drawing straight lines between each pixel value, we can recreate the spline in an image.
            firsthit = False
            lineting = []  # keeps pycharm happy
            for element in thelist:
                if firsthit is True:
                    # drawing the line takes int's in tuple form.
                    lineting = (lineting[0], lineting[1])
                    elementa = (element[0], element[1])
                    cv2.line(img=image, pt1=lineting, pt2=elementa, color=255, thickness=5)
                    lineting = element
                else:
                    lineting = element
                    firsthit = True

            # we draw the circles where we found them.
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(image, (x, y), r, 125,4)

        return cqpx(cv2.rotate(image,cv2.ROTATE_90_COUNTERCLOCKWISE))
