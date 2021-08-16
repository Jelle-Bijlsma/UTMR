import numpy as np
from PyQt5 import QtGui, QtWidgets
import cv2
from scipy import interpolate


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
        return cv2.Canny(image, para_canny[1], para_canny[2]), True
    elif true_sobel:
        return do_sobel(image, para_sobel[1:]), True
    else:
        return image, False
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

def do_morph(img, morph_vars, no_edgefinding):
    morph_com = morph_vars[0][1]
    morph_txt = morph_vars[0][1]
    valid_ops: list = morph_vars[1]
    checkbox: QtWidgets.QCheckBox = morph_vars[2]

    #print(f"we got morph_vars[0] it is: {morph_vars[0]}, and its type is {type(morph_vars[0])}")

    if morph_vars[0][0] is True:
        if (no_edgefinding == np.bool_(False)):
            cur_ele = np.copy(img)
            for element in morph_txt.split('\n'):
                try:
                    starter = element.split(' ')
                    kernelsize = (int(starter[2]), int(starter[2]))
                    kernel = cv2.getStructuringElement(shape=int(starter[4]), ksize=kernelsize)
                except IndexError:
                    print("whoops jimbo")
                    return cur_ele
                if starter[0] == valid_ops[0]:  # dilate
                    cur_ele = cv2.dilate(cur_ele, kernel, iterations=1)
                elif starter[0] == valid_ops[1]:  # erosion
                    cur_ele = cv2.erode(cur_ele, kernel, iterations=1)
                elif starter[0] == valid_ops[2]:  # m_grad
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_GRADIENT, kernel)
                elif starter[0] == valid_ops[3]:  # blackhat
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_BLACKHAT, kernel)
                elif starter[0] == valid_ops[4]:  # whitehat
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_TOPHAT, kernel)
            return cur_ele
        elif (no_edgefinding == np.bool_(True)):
            print("do canny first!")
            checkbox.setChecked(False)
            return img
        else:
            raise Exception("np.bool_ is different from python bool!")
    else:
        # print("no morph today")
        return img


def flood(img,original,params):
    checkbox: QtWidgets.QCheckBox = params[0]
    coords = params[1]

    if checkbox.isChecked():
        if coords is None:
            print("Please click the to-be flooded area first")
            checkbox.setChecked(False)
            return np.zeros((10,10),dtype='uint8'), img

        x,y = coords
        after_fill = np.copy(img)
        before_fill = np.copy(img)
        h, w = img.shape
        # print(f"h:{h}, w:{w}")
        mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(after_fill, mask, (x, y), 255)
        mask = after_fill ^ before_fill
        masked = mask & original

        return mask,masked
    else:
        return np.zeros((10, 10),dtype='uint8'), img

def circlefind(parameters: list, image: np.ndarray):
    circ_bool = parameters[0]
    dp = parameters[1] / 25  # since PyQt does not allow for non int slider values, they have to be created.
    minDist = parameters[2]
    param1 = parameters[3]
    param2 = parameters[4]
    minradius = parameters[5]
    maxradius = parameters[6]

    if circ_bool is False:
        return image

    imagepre = cv2.rotate(np.copy(image), cv2.ROTATE_90_CLOCKWISE)
    x,y = imagepre.shape
    scalefactor = 4
    imagez = cv2.resize(imagepre,(y*scalefactor,x*scalefactor))
    circles = cv2.HoughCircles(imagez, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist, param1=param1, param2=param2,
                               minRadius=minradius, maxRadius=maxradius)

    if circles is not None:
        # since the hough detects the circles randomly, we have the need to sort them in ascending order
        # for the spline to work
        if len(circles[0]) < 2:
            print(f"not enough circles {circles}")
            print(len(circles[0]))
            return image
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
                cv2.line(img=imagez, pt1=lineting, pt2=elementa, color=255, thickness=5)
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
            cv2.circle(imagez, (x, y), r, 125,4)

    return cv2.rotate(imagez,cv2.ROTATE_90_COUNTERCLOCKWISE)