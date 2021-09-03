import numpy as np
import cv2

""""
All the functions related to template matching
"""

def circlefind(parameters: list, image: np.ndarray):
    """
    Circlefinding is currently not used, but it would find all the coordinates of circles in an image
    :param parameters: parameters from circlefind group
    :param image:
    :return:
    """
    circ_bool = parameters[0]
    dp = parameters[1] / 25  # since PyQt does not allow for non int slider values, they have to be created.
    mindist = parameters[2]
    param1 = parameters[3]
    param2 = parameters[4]
    minradius = parameters[5]
    maxradius = parameters[6]

    if circ_bool is False:
        return image

    # image rotation is legacy, dont ask why I did it. you dont have to.
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
    """
    Code responsible for template matching. It is not as interactive as the remaining part of the code,
    especially the template selection. Would be nice to do that through GUI as well.
    :param img:
    :param parameters:
    :param template_list:
    :return:  color img + rectangle, and list of coords
    """

    dobool = parameters[0]
    treshold = parameters[1] / 100
    w, h = img.shape
    plt_im = np.zeros((w, h, 3), dtype='uint8')

    # we make the img COLOR. great
    plt_im[:, :, 0] = img
    plt_im[:, :, 1] = img
    plt_im[:, :, 2] = img
    if dobool is False:
        return img, [0, 0]

    template_pos = []
    template_x = []
    template_y = []
    coord_list = []

    for template in template_list:
        # Save the x,y coordinates (CENTRE) of each template in a list
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
    """
    In template matching we set a low confidence, such that all the points can be matched. This however,
    creates a lot of matches for 1 marker. So this function, uses distance based algorithm to decide which
    points belong to the same marker.
    :param mylist: list of points
    :return: sorted list of points
    """
    if mylist == [0, 0]:
        return []
    mylist = list(dict.fromkeys(mylist))  # remove duplicates
    counter = 0
    rangez = 15  # rangez is the maximal distance points can be apart.
    batches = []


    real_coords = []
    my_smaller_list = mylist

    """
    my_smaller_list should contain all the points which have not been assigned to a 'main' point. As soon as 
    the list length == 0, it means all the points are assinged.
    """

    while True:
        fp = 0
        if len(my_smaller_list) == 0:
            batch = "done"
        else:
            """"
            -take the first element from my_smaller_list as a starting point:
            -ignore the first point (itself)
            -difference in length is sum of  absolute difference in x and y.
            -if diff < preset, add it to a new list (a batch)
            -subtract batch from my_smaller_list
            -repeat
            """
            ct = my_smaller_list[0]
            newlist = []
            for element in my_smaller_list:
                if fp == 0:
                    fp = 1
                    continue
                nt = element  # just renaming it for convenience.
                diff = abs(ct[0] - nt[0]) + abs(ct[1] - nt[1])
                if diff < rangez:
                    newlist.append(nt)
            newlist.append(ct)
            batch = newlist

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

    """Now batches is a list containing lists of closely lying coordinates. each element of the list is now
    averaged out and saved into a list called real_coords. which is finally returned."""
    for element in batches:
        # print(f"this is a batch{element}")
        asd = np.array(element)
        x, _ = asd.shape
        bigx = int((np.sum(asd[:, 0]) / x))
        bigy = int((np.sum(asd[:, 1]) / x))

        real_coords.append((bigx, bigy))

    return real_coords


def drawsq(img, coords, cirq=False):
    """
    This function used to have more functions, but now its just the 'cv2.circle' function wrapped.
    """
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