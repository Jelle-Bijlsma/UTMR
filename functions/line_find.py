import numpy as np
import cv2


def draw_bb(params, img, cp):
    # print(cp)
    if cp == [] or params[0] is False:
        return img
    dx, dy = params[-2:]
    # fp = [cp[0][1],-cp[0][0]]
    fp = [cp[0][0], cp[0][1]]
    # print(f"fp={fp}")
    # trans = (fp[1], -fp[0])
    return cv2.rectangle(img, (fp[0] - 7 - dx, fp[1] -7 - dy), (fp[0] + dx + 7, fp[1] +7 + dy), [112, 51, 173])


def takelines(params, cp, mask):
    # https://stackoverflow.com/questions/45322630/how-to-detect-lines-in-opencv

    if cp == [] or params[0] is False:
        return mask, []
    dx, dy = params[-2:]

    # reverse again since we use it to acces elements
    fp = [cp[0][0], cp[0][1]]

    kernel = cv2.getStructuringElement(shape=0, ksize=(2, 2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, kernel)

    xstart = fp[0] - 7 -dx
    ystart = fp[1] -7 - dy

    xend = fp[0] + dx + 7
    yend = fp[1] + dy + 7

    mask_crop = mask[ystart:yend, xstart:xend]

    rho = params[1]
    theta = params[2] / 1000
    threshold = params[3]
    min_line_length = params[4]
    max_line_gap = params[5]

    lines = cv2.HoughLinesP(mask_crop, rho, theta, threshold, np.array([]),
                            min_line_length, max_line_gap)

    # print(mask_crop.shape)

    anglist = []

    """"
    Angle calculation is correct in this scenario but not robust to change. 
    Due to lines running in different directions and absolute measurements.
    Would need to do some coordinate transforms on the points
    """

    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                # print(f"point 1 {x1}, {y1}, point2 {x2}, {y2}")
                # cv2.line(mask_crop, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.line(mask_crop, (x1, y1), (x2, y2), 122, 3)
                # mask_crop = cv2.circle(mask_crop, (30,0), 10, (250))
                anglist.append(abs((np.arctan((y1 - y2) / (x1 - x2 + 0.0001)) / np.pi) * 180))
                # print(f"atan = {np.arctan((y1-y2)/(x1-x2+0.0001))}")

    # print(anglist)
    # print(f"wall angle{np.mean(anglist)}")
    x1, y1 = cp[0]
    # print(cp[0])
    x2, y2 = cp[4]
    # print(cp[4])
    tip_angle = (((np.arctan(((y1 - y2)) / ((x1 - x2)))) / np.pi) * 180)
    wall_angle = np.mean(anglist)

    return mask_crop, [tip_angle, wall_angle]
