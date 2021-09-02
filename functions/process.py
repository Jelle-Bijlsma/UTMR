import time
import warnings

import numpy as np
from PyQt5 import QtGui, QtWidgets
import cv2
from scipy import interpolate

def change_qpix(frame: np.ndarray):
    # some links i might need later
    # https://gist.github.com/belltailjp/a9538aaf3221f754e5bf

    # takes a frame and transforms it into qpix format. can take all datatypes.
    x = frame.shape
    if x == (0,):
        # print('empty ')
        # initialisation clause. When called with an empty array, the frame will be set to an empty 100,100.
        frame = np.zeros([100, 100], dtype='uint8')

    if frame.dtype != np.uint8:  # this check is very important. Frames already in uint8 will go to zero if
        frame_normalized = (frame * 255) / np.max(frame)  # normalized like this
        frame = frame_normalized.astype(np.uint8)

    if len(frame.shape) == 2:
        w, h = frame.shape
        qim = QtGui.QImage(frame.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
    else:
        w, h, c = frame.shape
        # print(frame.shape)
        if c == 3:
            qim = QtGui.QImage(frame.data.tobytes(), h, w, frame.strides[0], QtGui.QImage.Format_RGB888)
            # print("we in rgb")
        elif c == 1:
            qim = QtGui.QImage(frame.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
        else:
            raise Exception("QPIX problems")
    return QtGui.QPixmap.fromImage(qim)

def float_uint8(fft_frame):
    if fft_frame.dtype == np.dtype('float64'):
        # doing this, seems to behave like a histogram equalization. Is there another way?
        frame_normalized = (fft_frame * 255) / np.max(fft_frame)  # normalized like this
        frame = frame_normalized.astype(np.uint8)
    elif fft_frame.dtype == np.dtype('complex128'):
        fft_frame = fft_frame.real
        frame_normalized = (fft_frame * 255) / np.max(fft_frame)
        frame = frame_normalized.astype(np.uint8)

    elif fft_frame.dtype == np.dtype('uint8'):
        raise ValueError("expected float, got uint8?!")
    else:
        print("wrong datatype!")
        frame_normalized = (fft_frame * 255) / np.max(fft_frame)  # normalized like this
        frame = frame_normalized.astype(np.uint8)
    return frame

def calc_gls(image, parameters):
    """"
    The calc_GLS provides settings on the brightness. Besides doing graylevel slicing it also calculates the
    histogram.
    """

    # easy reading by pulling the new slice parameters apart.
    bval = parameters[0]
    boost = parameters[1]
    lbound = parameters[2]
    rbound = parameters[3]

    # Brightness adjustment
    if bval > 0:
        image_gls = np.where((255 - image) < bval, 255, image + bval)
    else:
        image_gls = np.where((image + bval) < 0, 0, (image + bval))
    # Gray level slicing
    # set to int16 to prevent rollover.
    image_gls = image_gls.astype(np.int16)
    temp = np.where((image_gls >= lbound) & (image_gls <= rbound), image_gls + boost, image_gls)
    temp = np.where(temp > 255, 255, temp)
    gls = np.where(temp < 0, 0, temp).astype('uint8')  # and bring it back to uint8
    # print("gls calc")

    l, b = gls.shape
    img2 = np.reshape(gls, l * b)
    # taking the log due to the huge difference between the amount of completely black pixels and the rest
    # adding + 1 else taking the log is undefined (10log1) = ??
    histogram = np.log10(np.bincount(img2, minlength=255)+1)
    # min length else you will get sizing errors.

    return gls, histogram

