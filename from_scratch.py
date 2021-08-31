import time

import cv2
import numpy as np
import os
# import matplotlib.pyplot as plt


mask = np.loadtxt('/home/jelle/PycharmProjects/UTMR/mask.txt')

thelist = [(81, 76), (85, 83), (89, 91), (91, 99), (93, 107), (94, 115), (95, 123), (95, 130), (95, 138), (94, 146),
           (93, 154), (92, 162), (90, 170), (89, 177), (88, 185), (86, 193), (85, 201), (83, 209), (82, 217), (80, 225)]

for element in thelist:
    mask = cv2.circle(mask,element,5,0)

cv2.imshow('cirq',mask)
cv2.waitKey(0)