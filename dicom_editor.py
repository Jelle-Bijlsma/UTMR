import os
from pydicom import dcmread
import matplotlib.pyplot as plt


def dicom_editor(choice):
    # choice = 0, show movie
    # choice = 1, make png
    filelist = os.listdir("./dicom/")
    filelist.sort()
    fps = 1 / 15

    if choice == 1:
        pngpath = "./dicom/png/"
        # if the png save path doesn't exist, create it.
        if not os.path.exists(pngpath):
            os.mkdir(pngpath)

    for element in filelist:
        # disregard non-dicom files
        if element[0:3] != 'IM_':
            continue

        # read file and put it in a use-able array
        string = "./dicom/" + element
        dicom = dcmread(string)
        array = dicom.pixel_array
        plt.imshow(array, cmap="gray")

        if choice == 1:
            savestring = "./dicom/png/" + element + ".png"
            plt.savefig(savestring)

        if choice == 0:
            # if blocking is true, rest of the code stops until the figure is closed.
            plt.show(block=False)
            plt.pause(fps)
