import time

import cv2
import numpy as np
import os
# import matplotlib.pyplot as plt

stepbystep = True

mask = np.loadtxt('/home/jelle/PycharmProjects/UTMR/mask.txt')
kernel = cv2.getStructuringElement(shape=0, ksize=(2, 2))
mask = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, kernel)

thelist = [(81, 76), (85, 83), (89, 91), (91, 99), (93, 107), (94, 115), (95, 123), (95, 130), (95, 138), (94, 146),
           (93, 154), (92, 162), (90, 170), (89, 177), (88, 185), (86, 193), (85, 201), (83, 209), (82, 217), (80, 225)]

""""
What is the concept:
        -remake dist determine
"""




def dist_determine(point,mask):
    xcent, ycent = point

    # instead of drawing a full circle, draw a spare one, consisting of 4 lines at
    # 0 degree (horizontal)
    # 30 degree
    # 60 degree
    # 90 degree (vertical)

    # predefine so we are FAST!
    # remember x = r*cos(theta) and y = r*sin(theta)
    val1 = 0.866  # cos(30), sin(60) sqrt(3)/2
    val2 = 0.5    # cos(60), sin(30)

    points = [tuple, tuple, tuple,
              tuple, tuple, tuple,
              tuple, tuple, tuple,
              tuple, tuple, tuple]

    for r in range(1,100):  # r for radius
        sq = int(val1 * r)
        h = int(val2 * r)
        # quadrant 1
        points[0] = (r+xcent, 0+ycent)
        points[1] = (sq+xcent,h+ycent)
        points[2] = (h+xcent,sq+ycent)
        # quadrant 2
        points[3] = (0+xcent,r+ycent)
        points[4] = (-sq+xcent,h+ycent)
        points[5] = (-h+xcent,sq+ycent)
        # quadrant 3
        points[6] = (-r+xcent,0+ycent)
        points[7] = (-sq+xcent,-h+ycent)
        points[8] = (-h+xcent,-sq+ycent)
        # quadrant 4
        points[9] = (0+xcent,-r+ycent)
        points[10] = (h+xcent,-sq+ycent)
        points[11] = (sq+xcent,-h+ycent)

        if r > 24:
            print(points)

        for ii in range(11):
            # gotta switch em w.r.t. array!
            if mask[(points[ii][1],points[ii][0])] == 255:
                return points[ii],r


print(dist_determine(thelist[0],mask))

vmask = np.copy(mask)

if stepbystep:
    for element in thelist:
        mask = cv2.circle(mask,element,5,255)
        print(f"doing point{element}")
        # There should be a better method than passing the entire mask all the time
        _, pointz = dist_determine(element,vmask)
        mask = cv2.line(mask,element,pointz,255)

    cv2.imshow('cirq',mask)
    cv2.waitKey(0)


def display_time():
    # in the case of SMALL opps, python is a few orders faster than numpy ;-)
    t1 = time.perf_counter()
    for i in range(1000):
        a = np.array([5.24])
        b = a
        c=a+b
    t2 = time.perf_counter()

    t3 = time.perf_counter()
    for i in range(1000):
        a = 5.24
        b = a
        c=a+b
    t4 = time.perf_counter()

    print(f"numpy took {t2-t1}, and python {t4-t3}")