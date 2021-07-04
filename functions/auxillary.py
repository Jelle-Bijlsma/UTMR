import os
import cv2
from pydicom import dcmread
import matplotlib.pyplot as plt


def png2avi(path,fps):
    # them ting be needing PNG
    filelist = os.listdir(path)
    filelist.sort()
    img_array = []
    for element in filelist:
        # print(element)
        fp = path + element
        img = cv2.imread(fp)
        h, w, l = img.shape
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


def dicom2png(filelist,path,project_name):
    a = 0
    for element in filelist:
        a = a +1
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