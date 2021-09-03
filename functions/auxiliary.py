import os
import cv2
from pydicom import dcmread
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets

"""
functions used in the dicom-editor/file loader
"""


def png2avi(path: str, fps: int) -> None:
    """Create a list of the PNG's in path, use cv2 videowriter to make it into a movie."""
    filelist = os.listdir(path)
    filelist.sort()
    img_array = []
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
    # fourcc: 4 bytes to identify videostreams.
    return


def dicom2png(filelist: list, path: str, project_name: str) -> int:
    """"extracts the png part out of the dicom images.
    File should start with 'IM_' """
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
    # count how many pngs are in the filelist.
    a = 0
    for element in filelist:
        if ".png" in element:
            a += 1
    return a


def popupmsg(text: str, iswhat: str):
    """"create a popup message. Can be generalized to do more than warnings
    currently supports only warning"""
    msg = QtWidgets.QMessageBox()
    msg.setText(text)
    if iswhat == "warning":
        msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.exec_()
    return


def loadin(filelist: list, path: str, size: list) -> list:
    # load grayscale png from list, given path.
    path = path + "/"
    imlist = []
    for element in filelist:
        # cp: current path
        cp = path + element
        # 0 indicates grayscale
        im = cv2.imread(cp, 0)
        # resize happens here
        im = im[size[0]:size[1], size[2]:size[3]]
        # im = im[58:428, 143:513]
        imlist.append(im)
    return imlist
