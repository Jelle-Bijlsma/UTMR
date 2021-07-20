import cv2
import numpy as np
from scipy.interpolate import interp1d
from scipy import interpolate

import matplotlib.pyplot as plt

window_name = 'Image'
radius = 10
thickness = 2
dx = 50
dy = 50
border = [0, 500]

seed_x = np.random.randint(50, 450)
seed_y = np.random.randint(50, 100)
coordinates = [seed_x, seed_y]

dp = 45 / 25
minDist = 11
param1 = 35 / 10
param2 = 22
minradius = 10
maxradius = 15

def grabfirst(alist: list, integer: int):
    return [item[integer] for item in alist]


while True:
    image = np.zeros([500, 500], np.uint8)
    seed_x = np.random.randint(50, 450)
    seed_y = np.random.randint(50, 100)

    coordinates = [seed_x, seed_y]

    for element in range(1, 10):
        coord_add_x = np.random.randint(-dx, dy)
        coord_add_y = np.random.randint(20, dy)
        coord_add = np.stack((coord_add_x, coord_add_y))
        # print(coord_add)
        coordinates = [sum(x) for x in zip(coordinates, coord_add)]
        # for element in centre_list:
        # print(coordinates)
        # abc = np.column_stack((coordinates[0], coordinates[1]))
        # print(abc[0])
        # image = cv2.circle(img=image, center=abc, radius=radius, color=255, thickness=thickness)
        image = cv2.circle(img=image, center=coordinates, radius=radius, color=255, thickness=thickness)



    size = (10, 10)
    image = np.transpose(cv2.blur(image, size))
    # cv2.imshow("output", image)
    output = image.copy()
    cv2.waitKey(0)
    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist, param1=param1, param2=param2,
                               minRadius=minradius, maxRadius=maxradius)
    print(circles)
    x = circles[0,:,0]
    x = np.reshape(x, [len(x), 1])
    print(x)
    y = circles[0,:,1]
    y = np.reshape(y, [len(y), 1])
    print(y)

    conlist = np.concatenate([x,y],axis=1)
    #print(conlist)

    mysort = sorted(conlist, key=lambda p: p[0])
    #print(mysort)
    x = grabfirst(mysort, 0)
    y = grabfirst(mysort, 1)

    f = interp1d(x, y)
    f2 = interp1d(x, y, kind='cubic')
    tck = interpolate.splrep(x, y, s=10)
    xnew = np.linspace(np.min(x), np.max(x), num=60, endpoint=True)
    spl = interpolate.InterpolatedUnivariateSpline(x, y, k=2)
    spl.set_smoothing_factor(0.5)
    xnew2 = np.linspace(np.min(x)-20, np.max(x)+20, num=60, endpoint=True)
    ynew2 = spl(xnew2)

    coords = np.array([[]])

    pcr = False
    for x,y in zip(xnew2,ynew2):
        if pcr is True:
            small = np.concatenate([small,np.array([[x,y]])])
        else:
            small = np.array([[x,y]])
            pcr = True
        # coords = np.concatenate([coords,small])
        # print(coords)

    thelist = np.round(small)

    pcr = False
    for element in thelist:
        if pcr is True:
            lineting = (int(lineting[0]), int(lineting[1]))
            elementa = (int(element[0]), int(element[1]))
            print(type(lineting))
            cv2.line(img=output,pt1=lineting,pt2=elementa,color=255,thickness=5)
            lineting = element
        else:
            lineting = element
            pcr = True

    # ynew = interpolate.splev(xnew, tck, der=0)
    #
    # plt.plot(x, y, 'o', xnew, f(xnew), '-', xnew, f2(xnew), '--', xnew, ynew, 'x')
    # plt.plot(x, y, 'o', xnew, f(xnew), '-', xnew, f2(xnew), '--', xnew2, spl(xnew2), 'x')
    # plt.legend(['data', 'linear', 'cubic', 'cubic_spline'], loc='best')
    # plt.show()

    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, 255, 4)
            # cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        # show the output image

        cv2.imshow("output", np.hstack([image, output]))
        cv2.waitKey(0)
    #


