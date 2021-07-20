import cv2
import numpy as np
from scipy.interpolate import interp1d
from scipy import interpolate


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

def grabfirst(alist: list, integer: int):
    return [item[integer] for item in alist]

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

        # print(type(image))
        # image = np.ndarray.astype(image,'uint8')
        # print(type(image))
        # blur = cv2.GaussianBlur(noisy, (3, 3), 1)
        # image = np.ndarray.astype(blur,'uint8')

    size = (10, 10)
    image = cv2.blur(image, size)
    row, col = image.shape
    mean = 0
    var = 0.1
    sigma = var ** 0.5

    for element in range(0,4):
        gauss = np.random.normal(mean, sigma, (row, col))
        gauss = gauss.reshape(row, col)
        noisy = np.ndarray.astype(gauss, 'uint8')
        image += noisy

    return image


def update(image, parameters):
    dp = parameters[0]/25
    minDist = parameters[1]
    param1 = parameters[2]/10
    param2 = parameters[3]
    minradius = parameters[4]
    maxradius = parameters[5]
    image = np.transpose(image)
    output = image.copy()


    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist, param1=param1, param2=param2,
                               minRadius=minradius, maxRadius=maxradius)
    print(circles.shape)

    print(circles)
    x = circles[0,:,0]
    x = np.reshape(x, [len(x), 1])
    print(x)
    y = circles[0,:,1]
    y = np.reshape(y, [len(y), 1])
    print(y)

    conlist = np.concatenate([x,y],axis=1)
    #print(conlist)

    mysort = sorted(conlist, key=lambda p: p[0])
    #print(mysort)
    x = grabfirst(mysort, 0)
    y = grabfirst(mysort, 1)

    f = interp1d(x, y)
    f2 = interp1d(x, y, kind='cubic')
    tck = interpolate.splrep(x, y, s=10)
    xnew = np.linspace(np.min(x), np.max(x), num=60, endpoint=True)
    spl = interpolate.InterpolatedUnivariateSpline(x, y, k=2)
    spl.set_smoothing_factor(0.5)
    xnew2 = np.linspace(np.min(x)-20, np.max(x)+20, num=60, endpoint=True)
    ynew2 = spl(xnew2)

    coords = np.array([[]])

    pcr = False
    for x,y in zip(xnew2,ynew2):
        if pcr is True:
            small = np.concatenate([small,np.array([[x,y]])])
        else:
            small = np.array([[x,y]])
            pcr = True
        # coords = np.concatenate([coords,small])
        # print(coords)

    thelist = np.round(small)

    pcr = False
    for element in thelist:
        if pcr is True:
            lineting = (int(lineting[0]), int(lineting[1]))
            elementa = (int(element[0]), int(element[1]))
            print(type(lineting))
            cv2.line(img=output,pt1=lineting,pt2=elementa,color=255,thickness=5)
            lineting = element
        else:
            lineting = element
            pcr = True


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
