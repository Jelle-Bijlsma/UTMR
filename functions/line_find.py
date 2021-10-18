import numpy as np
import cv2

""""
Notice how some functions have a 'tpz' variable. this is needed due to the offset of the template.
Currently you need to implement these new templates by hand.
This can be improved by creating a template class which hosts the dimensions and instances can be passed
arround such that template_1.offset could give the correct dimensions. Also GUI option for template match

"""

def draw_bb(params, img, cp):
    """"
    Draws a bounding box for the line finding. We only care for the wall-angle near the tip.
    params:list with last two values containing bounding box size
    img: image to draw on
    cp: list of coordinates
    return: drawn image
    """
    tpz = 7  # template size
    if cp == [] or params[0] is False:
        return img
    dx, dy = params[-2:]
    # fp = [cp[0][1],-cp[0][0]]
    fp = [cp[0][0], cp[0][1]]
    # print(f"fp={fp}")
    # trans = (fp[1], -fp[0])
    return cv2.rectangle(img, (fp[0] - tpz - dx, fp[1] -tpz - dy), (fp[0] + dx + tpz, fp[1] +tpz + dy),
                         [112, 51, 173])


def takelines(params, cp, mask):
    """
    How to detect the wall angle? We take the first detect point(i.e. the top point), and use the
    bounding box parameters to take a slice out of the mask. From this slice, lines are determined.
    Their angle is then calculated and averaged. This approach does not work for junctions yet.
    :param params: parameters with keyword 'lf'
    :param cp: (x,y) coordinates of markers
    :param mask:
    :return: cropped mask (img) and [tip_angle wall_angle] list
    """
    # https://stackoverflow.com/questions/45322630/how-to-detect-lines-in-opencv


    tpz = 7

    if cp == [] or params[0] is False:
        return mask, []
    dx, dy = params[-2:]

    fp = [cp[0][0], cp[0][1]]
    kernel = cv2.getStructuringElement(shape=0, ksize=(2, 2))
    # we do a morph gradient to get the OUTLINEs of the mask (which is filled)
    mask = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, kernel)

    xstart = fp[0] - tpz -dx
    ystart = fp[1] -tpz - dy

    xend = fp[0] + dx + tpz
    yend = fp[1] + dy + tpz

    mask_crop = mask[ystart:yend, xstart:xend]

    rho = params[1]
    theta = params[2] / 1000
    threshold = params[3]
    min_line_length = params[4]
    max_line_gap = params[5]

    lines = cv2.HoughLinesP(mask_crop, rho, theta, threshold, np.array([]),
                            min_line_length, max_line_gap)


    """"
    Angle calculation is correct in this scenario but not robust to change. 
    Due to lines running in different directions and absolute measurements.
    Would need to do some coordinate transforms on the points
    """

    anglist = []
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(mask_crop, (x1, y1), (x2, y2), 122, 3)
                anglist.append(abs((np.arctan((y1 - y2) / (x1 - x2 + 0.0001)) / np.pi) * 180))

    x1, y1 = cp[0]
    x2, y2 = cp[4]
    try:
        tip_angle = (((np.arctan(((y1 - y2)) / ((x1 - x2)))) / np.pi) * 180)
    except ZeroDivisionError:
        print("you tried to divide by zero, so we set tip angle to zero for u to prevent errors")
        tip_angle = 0
    wall_angle = np.mean(anglist)

    return mask_crop, [tip_angle, wall_angle]
