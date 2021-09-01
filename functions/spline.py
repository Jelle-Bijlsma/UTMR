import time
import warnings

import numpy as np
import cv2
from scipy import interpolate


def get_spline(keypoints, image, parameters=None):
    if parameters is None:
        return []

    # since the hough/template matching detects the circles randomly, we need to sort
    # them in ascending order for the spline to work
    if len(keypoints) < 3:
        # print(f"not enough circles {circles}")
        # print(len(circles[0]))
        return []

    # cx, cy = (169,0)  # 170 length, point 169 to rotate arround because we start at 0.
    # M = np.round(cv2.getRotationMatrix2D((cx,cy), 90, 1))  # CCW is positive!
    # got the inspiration from https://www.pyimagesearch.com/2021/01/20/opencv-rotate-image/
    # print(np.round(M))
    h,w  = image.shape
    M = np.array(([[0, 1],
                   [-1, 0]]))
    conlist = []

    for point in keypoints:
        vert_point = np.reshape(np.array(point), (2, 1))
        new_point = M.dot(vert_point)
        new_point[1] += w - 1
        # you can do the dot if you extend vertpoint: [x,y,1]
        conlist.append((int(new_point[0]), int(new_point[1])))

    # print(f"conlist: {conlist}")
    mysort = sorted(conlist, key=lambda p: p[0])
    mysort = np.array(mysort)
    x = mysort[:, 0]
    y = mysort[:, 1]
    # create spline
    try:
        spl = interpolate.InterpolatedUnivariateSpline(x, y, k=2)
    except ValueError:
        warnings.warn("Warning: function (get_spline) exited prematurely:\n"
                      "this normally happens during initialization. If you get this message in any other situation "
                      "too many coordinates have been passed to the 'get_spline' function."
                      )
        return []

    spl.set_smoothing_factor(0.5)
    # by creating a dense line grid to plot the spline over, we get smooth output
    xnew2 = np.linspace(np.min(x), np.max(x), num=20, endpoint=True)
    ynew2 = spl(xnew2)

    # this construction turns the separate xnew2 and ynew2 into an array of like this:
    # [[x0, y0]
    # [x1, y1]] etc..
    thelist = np.array([[x, y] for x, y in zip(xnew2, ynew2)], dtype="int")
    # print(f"this is the list{thelist}")

    thelist_new = []

    cx, cy = (84.5, 84.5)  # 170 length, point 169 to rotate arround because we start at 0.
    Ms = np.round(cv2.getRotationMatrix2D((cx, cy), -90, 1))  # CCW is positive!

    for point in thelist:
        point = (*point, 1)
        vert_point = np.reshape(np.array(point), (3, 1))
        new_point = Ms.dot(vert_point)
        thelist_new.append((int(new_point[0]), int(new_point[1])))

    return thelist_new


def draw_spline(image, thelist, mask, parameter):
    if thelist == []:
        return image, []


    channel = np.copy(image)
    w, h = image.shape
    cimage = np.zeros((w, h, 3))

    cimage[:, :, 0] = channel
    cimage[:, :, 1] = channel
    cimage[:, :, 2] = channel


    # we now want to round the list, to make them into accessible pixel values for plotting.
    # by drawing straight lines between each pixel value, we can recreate the spline in an image.
    firstpoint = True
    point_1 = []  # keeps pycharm happy
    dist = []

    manager = iter(thelist)
    _ = next(manager)
    _ = next(manager)

    q = len(thelist)

    for coord_iteration in thelist:
        if firstpoint is True:
            point_1 = coord_iteration
            firstpoint = False
        elif firstpoint is False:
            # rotate counterclockwise so the top point of the tip is point1
            doneyet = next(manager, True)
            point_2 = coord_iteration
            # doneyet is implemented to make sure the tip and end have their distance measured at the right place
            # uncomment both cv2.line's to see
            if doneyet is True:
                colorz, distz, spoints = color_determine(point_2, mask, parameter)
                # cv2.line(img=cimage, pt1=point_2, pt2=spoints, color=[255,0,0], thickness=1)
            else:
                colorz, distz, spoints = color_determine(point_1, mask, parameter)
                #.line(img=cimage, pt1=point_1, pt2=spoints, color=[255,0,0], thickness=1)

            dist.append(distz)
            cv2.line(img=cimage, pt1=point_1, pt2=point_2, color=colorz, thickness=1)
            point_1 = point_2

    # print(dist)
    return cimage, dist


def color_determine(point, mask, parameter):
    #eh = time.perf_counter()
    spoints, radius = dist_determine(point, mask)
    #print(f"time2 took {(time.perf_counter() - eh) * 1000}")
    # print(parameter)

    safe = parameter[2]
    medium = parameter[3]
    danger = parameter[4]

    if not danger < medium < safe:
        warnings.warn("danger < medium < safe is not the case, fallback to defaults")
        safe = 18
        medium = 12
        danger = 4

    # safe space
    if radius >= safe:
        color = [0, 255, 0]
    # medium space
    elif (radius < safe) & (radius > danger):
        if radius >= medium:
            # dy = 0-1
            rc = -1 / (safe - medium)
            b = 1 - rc * medium
            scale = int(round((radius * rc + b) * 255))
            color = [scale, 255, 0]

        else:
            # dy = 1-0
            rc = 1 / (medium - danger)
            b = 0 - rc * danger
            scale = int(round((radius * rc + b) * 255))
            color = [255, scale, 0]
    else:
        color = [255, 0, 0]
    return color, radius, spoints


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

    return [], []
