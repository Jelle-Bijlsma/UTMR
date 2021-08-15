import numpy as np
from PyQt5 import QtGui, QtWidgets
import cv2

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


def para_zero(value, name, replacement=1):
    if value == 0:
        print(f"{name} cannot be zero, set to: {replacement}")
        return replacement
    return value


def b_filter(parameters, shape):
    truth, cutoff, order = parameters
    y_dim = para_zero(shape[0], "y in b_filter")
    x_dim = para_zero(shape[1], "x in b_filter")

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
    sigx = para_zero(sigx, "g_filter sigmax")
    sigy = para_zero(sigy, "g_filter sigmay")
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


def edge_call(boxes,image,para_canny,para_sobel):
    sobelbox = boxes[0]
    cannybox = boxes[1]


    true_canny = para_canny[0]
    true_sobel = para_sobel[0]

    if true_canny & true_sobel:
        sobelbox.setChecked(False)
        cannybox.setChecked(True)
        print("there can be only one! (edge finder)")

    if true_canny:
        return cv2.Canny(image, para_canny[1], para_canny[2])
    elif true_sobel:
        return do_sobel(image, para_sobel[1:])
    else:
        return image
        #raise Exception("how did you even get here? @edge_call")


def do_sobel(frame,parameters):
    """"
    Left this in as a separate function for possibility of doing

    """

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
    # print(f"sobel shape is{np.shape(grad_x)}")

    # return float_uint8(grad)
    return grad


def do_canny(parameters,frame):
    threshold1 = parameters[0]
    threshold2 = parameters[1]
    edges = cv2.Canny(frame, threshold1, threshold2)
    # print(f"canny shape is{np.shape(edges)}")

    # canny by default outputs 8bit.
    # https://docs.opencv.org/3.4/dd/d1a/group__imgproc__feature.html#ga04723e007ed888ddf11d9ba04e2232de
    return edges


def get_pixel(event):
    x = event.pos().x()
    y = event.pos().y()
    # h, w = self.CurMov.get_og_frame().shape
    # xtot = self.mr_image.width()
    # ytot = self.mr_image.height()
    # x = int((x / xtot) * w)
    # y = int((y / ytot) * h)
    print(f"rescaled x = {x}, rescaled y = {y}")
    coords = f"x:{x}, y:{y}"
    # self.coords = (x, y)
    # self.lineEdit_coords.setText(coords)

    def morphstring_add(self, stringz):
        """"
        function called when new text is added to the 'textEdit_morph' box in the morphology tab.
        TextColor is set to black, data is pulled from the 'spinBox' regarding kernel size
        and the comboBox for kernel shape.

        cv2.getStructuringElement uses a '0,1,2' notation for sq. rect. ellipse, thus the index of the
        dropdown menu corresponds to these.
        """
        self.textEdit_morph.setTextColor(QColor(0, 0, 0, 255))
        stringz += f" kernel: {self.spinBox.value()} shape: {self.comboBox.currentIndex()}"
        self.textEdit_morph.append(stringz)

    def startmorph(self):
        error = self.checkmorph()
        if error == 1:
            # if there is an error in the checker, uncheck the checkbox
            self.checkBox_morph.setChecked(True)
            self.morphstatus = False
            self.update_all_things()
            return

        # dont think this applies now..
        if self.checkBox_morph.isChecked() is not False:
            # if the code is called when the checkbox is unchecked, return
            self.morphstatus = False
            self.update_all_things()
            return

        self.morphstatus = True
        self.update_all_things()

    def checkmorph(self):
        """"
        Checking function to see if the operation is spelled correctly, and if not, color the corresponding
        operation red. The addition of kernel + size was done later, and thus no error checking exists for that
        yet..
        """
        errorcode = 0
        cursor_pos = 0
        clrR = QtGui.QColor(255, 0, 0, 255)
        clrB = QtGui.QColor(0, 0, 0, 255)
        cursor = self.textEdit_morph.textCursor()

        for element in self.textEdit_morph.toPlainText().split('\n'):
            # split the full textEdit_morph up into newlines
            starter = element.split(' ')
            # split the newlines up into words
            if starter[0] in self.valid_ops:
                # we color it black, in case it previously has been colored red.
                # could color all black on each iteration and recolor all the reds. too bad!
                cursor.setPosition(cursor_pos)
                cursor.movePosition(20, 1, 1)
                self.textEdit_morph.setTextCursor(cursor)
                self.textEdit_morph.setTextColor(clrB)
                cursor_pos += len(element) + 1
                # print(cursor_pos)
                cursor.setPosition(0)
                # calls to setTextCursor are made to move the cursor to the actual position on screen
                self.textEdit_morph.setTextCursor(cursor)
            else:
                # maybe move next 7 lines into morp, and call it for this 1 and the previous 1?
                cursor.setPosition(cursor_pos)
                cursor.movePosition(20, 1, 1)
                self.textEdit_morph.setTextCursor(cursor)
                self.textEdit_morph.setTextColor(clrR)
                cursor_pos += len(element) + 1
                cursor.setPosition(0)
                self.textEdit_morph.setTextCursor(cursor)
                print("something is wrong!!")
                errorcode = 1
        return errorcode
