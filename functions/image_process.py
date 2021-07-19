from PyQt5 import QtGui
import numpy as np


# def butter_filter(fft, cutoff, order):
def butter_filter(shape: tuple, cutoff: int, order: int):
    x_dim, y_dim = shape
    x_max = x_dim / 2
    y_max = y_dim / 2
    x = np.arange(-x_max, x_max, 1)
    y = np.arange(-y_max, y_max, 1)

    X, Y = np.meshgrid(x, y)

    xterm = 1/(np.sqrt(1+(X/cutoff)**(2*order)))
    yterm = 1/(np.sqrt(1+(Y/cutoff)**(2*order)))
    Z = (xterm+yterm)/2
    return Z


def gaus_filter(shape: tuple, a: float, sigx, sigy):
    x_dim, y_dim = shape
    x_max = x_dim / 2
    y_max = y_dim / 2
    x = np.arange(-x_max, x_max, 1)
    y = np.arange(-y_max, y_max, 1)

    X, Y = np.meshgrid(x, y)

    xterm = (X ** 2) / (2 * sigx ** 2)
    yterm = (Y ** 2) / (2 * sigy ** 2)
    Z = (a/100) * np.exp(-(xterm + yterm))
    return Z


def change_qpix(frame: np.array([])):
    # takes a frame and transforms it into qpix format. can take all datatypes.
    x = frame.shape
    if x == (0,):
        print('empty ')
        # initialisation clause. When called with an empty array, the frame will be set to an empty 100,100.
        frame = np.zeros([100, 100], dtype='uint8')
    if frame.dtype != np.uint8:  # this check is very important. Frames already in uint8 will go to zero if
        frame_normalized = (frame * 255) / np.max(frame)  # normalized like this
        frame = frame_normalized.astype(np.uint8)
    w, h = frame.shape
    qim = QtGui.QImage(frame.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
    return QtGui.QPixmap.fromImage(qim)


def calc_hist(frame: np.array([])):
    l, b = frame.shape
    img2 = np.reshape(frame, l * b)
    # taking the log due to the huge difference between the amount of completely black pixels and the rest
    # adding + 1 else taking the log is undefined (10log1) = ??
    histogram = np.log10(np.bincount(img2, minlength=255) + 1)
    # min length else you will get sizing errors.
    return histogram


def calc_fft(frame, qpix=False):
    # https://docs.opencv.org/4.5.2/de/dbc/tutorial_py_fourier_transform.html
    fft = np.fft.fft2(frame)  # outputs a float
    if qpix is False:
        return fft
    else:
        temp_fft = np.fft.fftshift(fft)
        fft_gl = np.log(np.abs(temp_fft)+5)
        return change_qpix(fft_gl)


def prep_fft(fft_frame):
    fft_shift = np.fft.fftshift(fft_frame)
    fft_gl = np.log(np.abs(fft_shift)+5)
    return fft_gl


def float_uint8(fft_frame):
    if fft_frame.dtype == np.dtype('float64'):
        frame_normalized = (fft_frame * 255) / np.max(fft_frame)  # normalized like this
        frame = frame_normalized.astype(np.uint8)
    else:
        print("wrong datatype!")
        frame = "wrong"
    return frame
