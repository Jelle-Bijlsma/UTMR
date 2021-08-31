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
                ye = time.perf_counter()
                colorz, distz, spoints = color_determine(point_2, mask, parameter)
                # cv2.line(img=cimage, pt1=point_2, pt2=spoints, color=[255,0,0], thickness=1)
                print(f"time1 took {(time.perf_counter() - ye) * 1000}")
            else:
                ye = time.perf_counter()
                colorz, distz, spoints = color_determine(point_1, mask, parameter)
                print(f"time1 took {(time.perf_counter() - ye) * 1000}")
                cv2.line(img=cimage, pt1=point_1, pt2=spoints, color=[255,0,0], thickness=1)

            dist.append(distz)
            cv2.line(img=cimage, pt1=point_1, pt2=point_2, color=colorz, thickness=1)
            point_1 = point_2

    # print(dist)
    return cimage, dist


def color_determine(point, mask, parameter):
    eh = time.perf_counter()
    spoints, radius = dist_determine(point, mask)
    print(f"time2 took {(time.perf_counter() - eh) * 1000}")
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


def dist_determine(point, mask):
    xcent, ycent = point
    checkvar = 0
    mask = np.transpose(mask)
    for radius in range(1, 100):
        rstep = int(radius / 2)

        # horizontal
        y = 0
        yp = y + ycent
        x = int((radius ** 2 - (yp - ycent) ** 2) ** 0.5)
        iy = int(y)

        if mask[(x + xcent, iy + ycent)] == checkvar:
            return (x + xcent, iy + ycent), radius
        if mask[(-x + xcent, iy + ycent)] == checkvar:
            return (-x + xcent, iy + ycent), radius

        # the vertical lines
        y = radius
        yp = y + ycent
        x = int((radius ** 2 - (yp - ycent) ** 2) ** 0.5)
        iy = int(y)
        if mask[(x + xcent, iy + ycent)] == checkvar:
            return (x + xcent, iy + ycent), radius
        if mask[(-x + xcent, -iy + ycent)] == checkvar:
            return (x + xcent, -iy + ycent), radius

        # upper diagonal
        y = rstep
        yp = y + ycent
        x = int((radius ** 2 - (yp - ycent) ** 2) ** 0.5)
        iy = int(y)

        if mask[(x + xcent, iy + ycent)] == checkvar:
            return (x + xcent, iy + ycent), radius

        if mask[(-x + xcent, iy + ycent)] == checkvar:
            return (-x + xcent, iy + ycent), radius

        if mask[(x + xcent, -iy + ycent)] == checkvar:
            return (x + xcent, -iy + ycent), radius

        if mask[(-x + xcent, -iy + ycent)] == checkvar:
            return (-x + xcent, -iy + ycent), radius

        # the lower diagonals
        y = int(radius - rstep * 0.25)
        yp = y + ycent
        x = int((radius ** 2 - (yp - ycent) ** 2) ** 0.5)
        iy = int(y)

        if mask[(x + xcent, iy + ycent)] == checkvar:
            return (x + xcent, iy + ycent), radius

        if mask[(-x + xcent, iy + ycent)] == checkvar:
            return (-x + xcent, iy + ycent), radius

        if mask[(x + xcent, -iy + ycent)] == checkvar:
            return (x + xcent, -iy + ycent), radius

        if mask[(-x + xcent, -iy + ycent)] == checkvar:
            return (-x + xcent, -iy + ycent), radius

    return [], []
