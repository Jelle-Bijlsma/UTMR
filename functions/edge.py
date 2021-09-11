import numpy as np
from PyQt5 import QtWidgets
import cv2

""""
Collection where all the edge finding functions are stored (& flood function) and the 
core of the morphological operation.
"""

def edge_call(image, para_canny, para_sobel):
    """"
    Edge call is used to determine wheter canny is pressed, sobel, or both.
    """
    true_canny = para_canny[0]
    true_sobel = para_sobel[0]

    if true_canny & true_sobel:
        return do_canny(para_canny[1:], do_sobel(image, para_sobel[1:])), True

    if true_canny:
        return cv2.Canny(image, para_canny[1], para_canny[2]), True
    elif true_sobel:
        return do_sobel(image, para_sobel[1:]), True
    else:
        return image, False
        # raise Exception("how did you even get here? @edge_call")


def do_sobel(frame, parameters):
    """"
    Left this in as a separate function for possibility of doing separate sobel X, Y or a combination of them
    """

    ksize = parameters[0]
    scale = parameters[1]
    delta = parameters[2]

    grad_x = cv2.Sobel(frame, cv2.CV_16S, 1, 0, ksize=ksize, scale=scale, delta=delta,
                       borderType=cv2.BORDER_DEFAULT)
    grad_y = cv2.Sobel(frame, cv2.CV_16S, 0, 1, ksize=ksize, scale=scale, delta=delta,
                       borderType=cv2.BORDER_DEFAULT)

    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    # the gradient is shown in the main window, and in the third window we show the 'original' main
    # print(f"sobel shape is{np.shape(grad_x)}")

    # return float_uint8(grad)
    return grad


def do_canny(parameters, frame):
    threshold1 = parameters[0]
    threshold2 = parameters[1]
    edges = cv2.Canny(frame, threshold1, threshold2)
    # print(f"canny shape is{np.shape(edges)}")
    # canny by default outputs 8bit.
    # https://docs.opencv.org/3.4/dd/d1a/group__imgproc__feature.html#ga04723e007ed888ddf11d9ba04e2232de
    return edges


def do_morph(img, morph_vars, no_edgefinding):
    morph_txt = morph_vars[0][1]
    valid_ops: list = morph_vars[1]
    checkbox: QtWidgets.QCheckBox = morph_vars[2]


    if morph_vars[0][0] is True:
        if no_edgefinding == np.bool_(False):
            cur_ele = np.copy(img)
            for element in morph_txt.split('\n'):
                try:
                    starter = element.split(' ')
                    kernelsize = (int(starter[2]), int(starter[2]))
                    kernel = cv2.getStructuringElement(shape=int(starter[4]), ksize=kernelsize)
                except IndexError:
                    print("whoops jimbo")
                    return cur_ele
                if starter[0] == valid_ops[0]:  # dilate
                    cur_ele = cv2.dilate(cur_ele, kernel, iterations=1)
                elif starter[0] == valid_ops[1]:  # erosion
                    cur_ele = cv2.erode(cur_ele, kernel, iterations=1)
                elif starter[0] == valid_ops[2]:  # m_grad
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_GRADIENT, kernel)
                elif starter[0] == valid_ops[3]:  # blackhat
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_BLACKHAT, kernel)
                elif starter[0] == valid_ops[4]:  # whitehat
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_TOPHAT, kernel)
            return cur_ele
        elif no_edgefinding == np.bool_(True):
            print("do canny first!")
            checkbox.setChecked(False)
            return img
        else:
            raise Exception("np.bool_ is different from python bool!")
    else:
        # print("no morph today")
        return img


def flood(img, original, params):
    checkbox: QtWidgets.QCheckBox = params[0]
    coords = params[1]

    if checkbox.isChecked():
        if coords is None:
            print("Please click the to-be flooded area first")
            checkbox.setChecked(False)
            return np.zeros((10, 10), dtype='uint8'), img

        x, y = coords
        after_fill = np.copy(img)
        before_fill = np.copy(img)
        h, w = img.shape
        # print(f"h:{h}, w:{w}")
        mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(after_fill, mask, (x, y), 255)
        mask = after_fill ^ before_fill
        #mask = after_fill
        #kernel = cv2.getStructuringElement(shape=0,ksize=(3,3))
        #mask = cv2.erode(mask,kernel,iterations=1)
        #kernel = cv2.getStructuringElement(shape=0,ksize=(4,1))
        #mask = cv2.erode(mask,kernel,iterations=1)
        masked = mask & original

        return mask, masked
    else:
        return np.zeros((10, 10), dtype='uint8'), img
