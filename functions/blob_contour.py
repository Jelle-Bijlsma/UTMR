import cv2
import numpy as np

def contourr(im):
    ret, thresh = cv2.threshold(im, 127, 255, 0)
    # get contours
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours_area = []
    # calculate area and filter into new array
    for con in contours:
        area = cv2.contourArea(con)
        if 1000 < area < 10000:
            contours_area.append(con)

    contours_cirles = []

    # check if contour is of circular shape
    for con in contours_area:
        perimeter = cv2.arcLength(con, True)
        area = cv2.contourArea(con)
        if perimeter == 0:
            break
        circularity = 4 * 3.14159 * (area / (perimeter * perimeter))
        if 0.7 < circularity < 1.2:
            contours_cirles.append(con)

def blobf(im,para):
    params = cv2.SimpleBlobDetector_Params()
    # Change thresholds
    params.minThreshold = para[1]
    params.thresholdStep = para[-1]
    params.maxThreshold = para[6]
    # Filter by Area.
    params.filterByArea = True
    params.minArea = para[5]
    params.maxArea = para[10]
    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = para[4]/50
    params.maxCircularity = para[9]/50
    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = para[3]/50
    params.maxConvexity = para[8]/50
    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = para[2]/100
    params.maxInertiaRatio = para[7]/100

    detector = cv2.SimpleBlobDetector_create(params)  # only SimpleBlob
    keypoints = detector.detect(im)
    kpcoords = []
    if len(keypoints)>1:
        #print(type(keypoints[0]))
        for element in keypoints:
            kpcoords.append(element.pt)
        #print(kpcoords)
    return kpcoords, keypoints
    #print(keypoints)

    #im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (255),
    #                                      cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


    #cv2.imshow("Keypoints", im_with_keypoints)
    #cv2.waitKey(0)
