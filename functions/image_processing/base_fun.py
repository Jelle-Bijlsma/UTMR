import numpy as np
from PyQt5 import QtGui


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
    histogram = np.log10(np.bincount(img2, minlength=255) + 1)
    # min length else you will get sizing errors.

    return gls, histogram


def change_qpix(frame: np.array([])):
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
            qim = QtGui.QImage(frame.data.tobytes(), h, w, h * 4, QtGui.QImage.Format_RGB32)
        elif c == 1:
            qim = QtGui.QImage(frame.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
        else:
            raise Exception("QPIX problems")
    return QtGui.QPixmap.fromImage(qim)


def apply_filter(parameters, image, filterz, *args):
    truth = parameters[0]
    image_fft = np.fft.fft2(image)
    if not truth:
        return image, image_fft

    # filters come in the undeformed state, thus to properly multiply them, they have to be shifted
    fft_filtered_image = np.multiply(image_fft, np.fft.fftshift(filterz))
    filtered_image = np.fft.ifft2(fft_filtered_image)
    # fft_filtered and filtered return as complex 128

    return float_uint8(filtered_image), fft_filtered_image


def b_filter(parameters, shape):
    truth, cutoff, order = parameters
    y_dim, x_dim = shape
    x_max = x_dim / 2
    y_max = y_dim / 2
    x = np.arange(-x_max, x_max, 1)
    y = np.arange(-y_max, y_max, 1)

    X, Y = np.meshgrid(x, y)

    xterm = 1 / (np.sqrt(1 + (X / cutoff) ** (2 * order)))
    yterm = 1 / (np.sqrt(1 + (Y / cutoff) ** (2 * order)))
    Z = (xterm + yterm) / 2
    return Z

def g_filter(parameters, shape):
    truth, a, sigx, sigy = parameters
    y_dim, x_dim = shape
    x_max = x_dim / 2
    y_max = y_dim / 2
    x = np.arange(-x_max, x_max, 1)
    y = np.arange(-y_max, y_max, 1)

    X, Y = np.meshgrid(x, y)

    xterm = (X ** 2) / (2 * sigx ** 2)
    yterm = (Y ** 2) / (2 * sigy ** 2)
    Z = (a / 100) * np.exp(-(xterm + yterm))
    return Z


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


def prep_fft(fft_frame):
    fft_shift = np.fft.fftshift(fft_frame)
    fft_gl = np.log(np.abs(fft_shift) + 5)
    return fft_gl
