# import matplotlib.pyplot as plt # useful to make plots
# from pydicom import dcmread     # dicom library to read dicom
import os                       # scan all the dicom files
import cv2


path = "./dicom/png/"
filelist = os.listdir(path)
filelist.sort()

img_array = []

for element in filelist:
    print(element)
    fp = path + element
    img = cv2.imread(fp)
    h,w,l = img.shape
    # notice the reversal of order ...
    size = (w,h)
    img_array.append(img)

# constructor
out = cv2.VideoWriter('video.avi',cv2.VideoWriter_fourcc(*'FFV1'),15,size)
# fourcc: Een FourCC is een reeks van vier bytes gebruikt om dataformaten te identificeren.
# 15 is fps
# size is size of the video


for i in range(len(img_array)):
    out.write(img_array[i])
out.release()