import cv2
import numpy as np

# draw 10 random circles in an image. The

window_name = 'Image'
radius = 10
thickness = 2

while True:
    image = np.zeros([500, 500], np.uint8)
    centre_list = np.random.randint(1, 500, [10, 2])
    for element in centre_list:
        image = cv2.circle(img=image, center=element, radius=radius, color=255, thickness=thickness)
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
