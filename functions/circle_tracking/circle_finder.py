import cv2
import numpy as np

window_name = 'Image'
radius = 10
thickness = 2
dx = 50
dy = 50
border = [0, 500]


# three functions: new, find, show
# 'new' creates an image of a new set of circles
# 'find' creates an image with the found images from new
# 'show' shows whatever image


# draw 10 random circles in an image.
def new():
    image = np.zeros([500, 500], np.uint8)
    seed_x = np.random.randint(50, 450)
    seed_y = np.random.randint(50, 100)

    coordinates = [seed_x, seed_y]

    for element in range(1, 10):
        coord_add_x = np.random.randint(-dx, dy)
        coord_add_y = np.random.randint(20, dy)
        coord_add = np.stack((coord_add_x, coord_add_y))
        coordinates = [sum(x) for x in zip(coordinates, coord_add)]
        image = cv2.circle(img=image, center=coordinates, radius=radius, color=255, thickness=thickness)
        row, col = image.shape
        mean = 0
        var = 0.1
        sigma = var ** 0.5
        gauss = np.random.normal(mean, sigma, (row, col))
        gauss = gauss.reshape(row, col)
        noisy = np.ndarray.astype(gauss, 'uint8')
        image += noisy
        # print(type(image))
        # image = np.ndarray.astype(image,'uint8')
        # print(type(image))
        # blur = cv2.GaussianBlur(noisy, (3, 3), 1)
        # image = np.ndarray.astype(blur,'uint8')

    return image


def update(image, parameters):
    dp = parameters[0]/25
    minDist = parameters[1]
    param1 = parameters[2]/10
    param2 = parameters[3]
    minradius = parameters[4]
    maxradius = parameters[5]
    output = image.copy()
    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist, param1=param1, param2=param2,
                               minRadius=minradius, maxRadius=maxradius)
    print(circles.shape)

    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, 125, 4)
            # cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

    return np.hstack([image, output])


def random_noise(image, mode='gaussian', seed=None, clip=True, **kwargs):
    mode = mode.lower()
    if image.min() < 0:
        low_clip = -1
    else:
        low_clip = 0
    if seed is None:
        np.random.seed(seed=seed)

    if mode == 'gaussian':

        # https://stackoverflow.com/questions/54380447/error-using-houghcircles-with-3-channel-input
        noise = np.random.normal(kwargs['mean'], kwargs['var'] ** 0.5,
                                 image.shape)
        noise = np.ndarray.astype(noise, dtype='uint8')
        out = image + noise
        print(out.shape)
        print(out.dtype)
    if clip:
        out = np.clip(out, low_clip, 1.0)

    return out
