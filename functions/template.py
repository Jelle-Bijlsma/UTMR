import numpy as np
import cv2


def circlefind(parameters: list, image: np.ndarray):
    circ_bool = parameters[0]
    dp = parameters[1] / 25  # since PyQt does not allow for non int slider values, they have to be created.
    mindist = parameters[2]
    param1 = parameters[3]
    param2 = parameters[4]
    minradius = parameters[5]
    maxradius = parameters[6]

    if circ_bool is False:
        return image

    imagepre = cv2.rotate(np.copy(image), cv2.ROTATE_90_CLOCKWISE)
    x, y = imagepre.shape
    scalefactor = 4
    imagez = cv2.resize(imagepre, (y * scalefactor, x * scalefactor))
    circles = cv2.HoughCircles(imagez, cv2.HOUGH_GRADIENT, dp=dp, minDist=mindist, param1=param1, param2=param2,
                               minRadius=minradius, maxRadius=maxradius)
    circles = np.round(circles[0, :]).astype("int")
    # loop over the (x, y) coordinates and radius of the circles
    if circles is not None:
        for (x, y, r) in circles:
            print("drawing")
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(imagez, (x, y), r, 125, 4)

    return cv2.rotate(imagez, cv2.ROTATE_90_COUNTERCLOCKWISE)


def templatematch(img, parameters, template_list):
    _dobool = parameters[0]
    treshold = parameters[1] / 100
    # plt_im = np.copy(img)
    w, h = img.shape
    plt_im = np.zeros((w, h, 3), dtype='uint8')
    plt_im[:, :, 0] = img
    plt_im[:, :, 1] = img
    plt_im[:, :, 2] = img
    if _dobool is False:
        return img, [0, 0]

    template_pos = []
    template_x = []
    template_y = []
    coord_list = []

    for template in template_list:
        w, h = template.shape
        w2 = int(round(w/2))
        h2 = int(round(h/2))
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= treshold)
        template_x.append(loc[0])
        template_y.append(loc[1])
        template_pos.append(loc)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(plt_im, pt, (pt[0] + w, pt[1] + h), (200, 0, 0), 2)
            coord_list.append((pt[0] + w2, pt[1] + h2))
    return plt_im, coord_list


def sort_out(mylist):
    if mylist == [0, 0]:
        return []
    mylist = list(dict.fromkeys(mylist))  # remove duplicates
    counter = 0
    rangez = 15
    batches = []
    real_coords = []
    my_smaller_list = mylist

    while True:
        fp = 0
        if len(my_smaller_list) == 0:
            batch = "done"
        else:
            ct = my_smaller_list[0]
            newlist = []
            for element in my_smaller_list:
                if fp == 0:
                    fp = 1
                    continue
                nt = element
                diff = abs(ct[0] - nt[0]) + abs(ct[1] - nt[1])
                if diff < rangez:
                    newlist.append(nt)
            newlist.append(ct)
            batch = newlist
        # batch = get_a_batch(my_smaller_list, 7, counter)
        if len(batch) == 0:
            counter += 1
            continue
        elif batch == "done":
            break

        batches.append(batch)
        batch_set = set(batch)
        msl_set = set(my_smaller_list)
        msl_set = msl_set.difference(batch_set)
        my_smaller_list = list(msl_set)

    for element in batches:
        # print(f"this is a batch{element}")
        asd = np.array(element)
        x, _ = asd.shape
        bigx = int((np.sum(asd[:, 0]) / x))
        bigy = int((np.sum(asd[:, 1]) / x))

        real_coords.append((bigx, bigy))

    return real_coords


def drawsq(img, coords, cirq=False):
    if coords == []:
        return img
    if cirq is False:
        for x, y in coords:
            # one day, i need to fill in the actual template size..
            cv2.circle(img, (x, y),6,255,3)
    else:
        for x, y in coords:
            cv2.circle(img, (x, y), 4, [255, 0, 0])
    return img