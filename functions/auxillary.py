import os
import cv2
import numpy
from pydicom import dcmread
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtGui


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


def cv2qpix(im: numpy.ndarray):
    w, h = im.shape
    qim = QtGui.QImage(im.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
    return QtGui.QPixmap.fromImage(qim)


def qpixmaker(imlist: list):
    qpixarray = []
    for element in imlist:
        qpixarray.append(cv2qpix(element))
    return qpixarray

