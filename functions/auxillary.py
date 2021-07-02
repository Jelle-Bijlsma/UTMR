import os
import cv2


def getallfiles(self, path):
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
    return