import os
import cv2
from pydicom import dcmread
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtGui
import numpy as np


def png2avi(path: str, fps: int) -> None:
    # them ting be needing PNG
    filelist = os.listdir(path)
    filelist.sort()
    img_array = []
    # pre define to stop pycharm from whining
    size = (0, 0)

    for element in filelist:
        # print(element)
        fp = path + element
        img = cv2.imread(fp)
        h, w, trash = img.shape
        # notice the reversal of order ...
        size = (w, h)
        img_array.append(img)

    # check if list is nonempty
    # save location is still wrong!
    if filelist:
        out = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'FFV1'), fps, size)
        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release()
    # fourcc: Een FourCC is een reeks van vier bytes gebruikt om dataformaten te identificeren.
    return


def dicom2png(filelist: list, path: str, project_name: str) -> int:
    a = 0
    for element in filelist:
        a = a + 1
        # disregard non-dicom files
        if element[0:3] != 'IM_':
            continue

        # read file and put it in a use-able array
        string = path + element
        dicom = dcmread(string)
        array = dicom.pixel_array
        plt.imshow(array, cmap="gray")
        savestring = "./data/png/" + project_name + "/" + element + ".png"
        plt.savefig(savestring)

    return a


def checkifpng(filelist: list) -> int:
    a = 0
    for element in filelist:
        if ".png" in element:
            a += 1
    return a


def popupmsg(text: str, iswhat: str):
    msg = QtWidgets.QMessageBox()
    msg.setText(text)
    if iswhat == "warning":
        msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.exec_()
    return


def loadin(filelist: list, path: str) -> list:
    # load grayscale png from list, given path.
    path = path + "/"
    imlist = []
    for element in filelist:
        # cp: current path
        cp = path + element
        # 0 indicates grayscale
        im = cv2.imread(cp, 0)
        im = im[58:428, 143:513]
        imlist.append(im)
    return imlist


def butter_filter(fft, cutoff, order):
    x_dim, y_dim = np.shape(fft)
    x_max = x_dim / 2
    y_max = y_dim / 2
    x = np.arange(-x_max, x_max, 1)
    y = np.arange(-y_max, y_max, 1)

    X, Y = np.meshgrid(x, y)

    xterm = 1/(np.sqrt(1+(X/cutoff)**(2*order)))
    yterm = 1/(np.sqrt(1+(Y/cutoff)**(2*order)))
    Z = (xterm+yterm)/2
    return Z


def change_qpix(frame: np.array([])):
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
        fft_gl = 20 * np.log(np.abs(temp_fft))
        # i don't know about this chief.
        return change_qpix(fft_gl)
