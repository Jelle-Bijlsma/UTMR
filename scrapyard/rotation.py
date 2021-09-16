import numpy as np
import cv2

""""
Spline used to be done by means of rotation.. 
Since spline cannot handle situations in which yn_1 > yn_2 
by rotation 90 deg ccw we circumvent this problem. However, you could also swap X,Y. This realization I made
very late. Here is the code to do proper image rotation in CV2 since i thought it was quite counter intuitive. 

Made the functions now, didnt actually check if they work but this should give a general idea. 
"""


## TOWARDS
def do_ccw(image, keypoints):
    # cx, cy = (169,0)  # 170 length, point 169 to rotate arround because we start at 0.
    # M = np.round(cv2.getRotationMatrix2D((cx,cy), 90, 1))  # CCW is positive!
    # got the inspiration from https://www.pyimagesearch.com/2021/01/20/opencv-rotate-image/
    # print(np.round(M))

    h, w = image.shape
    M = np.array(([[0, 1],
                   [-1, 0]]))
    conlist = []

    for point in keypoints:
        vert_point = np.reshape(np.array(point), (2, 1))
        new_point = M.dot(vert_point)
        new_point[1] += w - 1
        conlist.append((int(new_point[0]), int(new_point[1])))
        # you can do the dot if you extend vertpoint: [x,y,1]


def do_cw(image,rot_keypoints):
    h, w = image.shape
    cx, cy = (round((w - 1) / 2), round((w - 1) / 2))  # 170 length, point 169 to rotate arround because we start at 0.
    Ms = np.round(cv2.getRotationMatrix2D((cx, cy), -90, 1))  # CCW is positive!

    thelist_new = []

    for point in rot_keypoints:
        point = (*point, 1)
        vert_point = np.reshape(np.array(point), (3, 1))
        new_point = Ms.dot(vert_point)
        thelist_new.append((int(new_point[0]), int(new_point[1])))
