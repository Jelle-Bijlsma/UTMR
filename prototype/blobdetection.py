import cv2
import numpy as np

im = cv2.imread("../data/png/mri31/RLI_JB_RAM_CATH_TRACKING.MR.ABDOMEN_LIBRARY.0031.0041.2021.09.02.15.32.11.998847.16889705.IMA.png", cv2.IMREAD_GRAYSCALE)
params = cv2.SimpleBlobDetector_Params()

# DO BLOB DETECTION??
# https://learnopencv.com/blob-detection-using-opencv-python-c/

# OR MAYBE CONTOUR:
# https://stackoverflow.com/questions/42203898/python-opencv-blob-detection-or-circle-detection


## manual ez sharpening or blurring?
#im = cv2.medianBlur(im,1)
filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
# Applying cv2.filter2D function on our Cybertruck image
im=cv2.filter2D(im,-1,filter)


"""
Thresholding : Convert the source images to several binary images by thresholding the source image with thresholds
    starting at minThreshold. These thresholds are incremented  by thresholdStep until maxThreshold.
    So the first threshold is minThreshold, the second is minThreshold + thresholdStep, the third is minThreshold +
    2 x thresholdStep, and so on.
 
Grouping : In each binary image,  connected white pixels are grouped together.  Let’s call these binary blobs.

Merging  : The centers of the binary blobs in the binary images are computed, and  blobs located
    closer than minDistBetweenBlobs are merged.
    
Center & Radius Calculation :  The centers and radii of the new merged blobs are computed and returned.
"""

# Change thresholds
params.minThreshold = 10
params.thresholdStep = 1
params.maxThreshold = 200
# Filter by Area.
params.filterByArea = True
params.minArea = 18
params.maxArea = 100
# Filter by Circularity
params.filterByCircularity = True
params.minCircularity = 0.05
# Filter by Convexity
params.filterByConvexity = True
params.minConvexity = 0.5
# Filter by Inertia
params.filterByInertia = True
params.minInertiaRatio = 0.2


detector = cv2.SimpleBlobDetector_create(params)  #only SimpleBlob
keypoints = detector.detect(im)

print(keypoints)

im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (255),
                                       cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

cv2.imshow("Keypoints", im_with_keypoints)
cv2.waitKey(0)
