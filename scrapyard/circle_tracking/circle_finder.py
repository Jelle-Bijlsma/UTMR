import cv2
import numpy as np
from scipy import interpolate

""""
The file which is responsible for the circle finding functions. Generates random circles and then
gaussian noise + blur. Then it uses hough transform to find the circles, and uses a quadratic spline to
fit a line through them.  
"""

# variables used circle generation
radius = 10
thickness = 2
dx = 50  # pixel distance with which the x-pos can change gradually
dy = 50  # pixel distance with which the y-pos can change gradually
border = [0, 500]

# noise variables
size = (10, 10)
mean = 0
var = 0.1
sigma = var ** 0.5


def new():
    # function draws 10 procedural circles in an image. Adds noise and gaussian blur.
    image = np.zeros([500, 500], np.uint8)
    # creates a bounding box for initial circle to spawn. caution: the image gets rotated 90 deg, so x and y are
    # switched in final presentation. This is due to spline not being happy with overlapping x values.
    seed_x = np.random.randint(50, 450)
    seed_y = np.random.randint(50, 100)
    coordinates = [seed_x, seed_y]

    for element in range(1, 10):
        coord_add_x = np.random.randint(-dx, dy)
        coord_add_y = np.random.randint(20, dy)  # set to 20 min to prevent circles from overlapping
        coord_add = np.stack((coord_add_x, coord_add_y))
        coordinates = np.add(coordinates, coord_add)
        image = cv2.circle(img=image, center=coordinates, radius=radius, color=255, thickness=thickness)

    image = cv2.blur(image, size)  # add blur
    row, col = image.shape

    for element in range(0, 4):
        # add 4 instances of gaussian blur
        gauss = np.random.normal(mean, sigma, (row, col))
        gauss = gauss.reshape(row, col)
        noisy = np.ndarray.astype(gauss, 'uint8')
        image += noisy

    return image  # end of function


def update(image, parameters):
    # update function finds the circles in image, given the hough parameters in list form.
    dp = parameters[0] / 25  # since PyQt does not allow for non int slider values, they have to be created.
    minDist = parameters[1]
    param1 = parameters[2] / 10
    param2 = parameters[3]
    minradius = parameters[4]
    maxradius = parameters[5]
    # image gets rotated 90 deg because of earlier mentioned spline problems.
    image = np.transpose(image)
    output = image.copy()  # keep a copy of image to be used later in stacking.
    # circles is a list of all the positions of circles it could find including their radius
    # [[x0,y0,r0]
    #  [x1,y1,r1]] etc
    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist, param1=param1, param2=param2,
                               minRadius=minradius, maxRadius=maxradius)
    if circles is not None:
        # since the hough detects the circles randomly, we have the need to sort them in ascending order
        # for the spline to work
        conlist = circles[0, :, 0:2]
        mysort = sorted(conlist, key=lambda p: p[0])
        mysort = np.array(mysort)
        x = mysort[:, 0]
        y = mysort[:, 1]
        # create spline
        spl = interpolate.InterpolatedUnivariateSpline(x, y, k=2)
        spl.set_smoothing_factor(0.5)
        # by creating a dense line grid to plot the spline over, we get smooth output
        xnew2 = np.linspace(np.min(x) - 20, np.max(x) + 20, num=60, endpoint=True)
        ynew2 = spl(xnew2)

        # this construction turns the separate xnew2 and ynew2 into an array of like this:
        # [[x0, y0]
        # [x1, y1]] etc..
        thelist = np.array([[x, y] for x, y in zip(xnew2, ynew2)], dtype="int")

        # we now want to round the list, to make them into accessible pixel values for plotting.
        # by drawing straight lines between each pixel value, we can recreate the spline in an image.
        firsthit = False
        lineting = []  # keeps pycharm happy
        for element in thelist:
            if firsthit is True:
                # drawing the line takes int's in tuple form.
                lineting = (lineting[0], lineting[1])
                elementa = (element[0], element[1])
                cv2.line(img=output, pt1=lineting, pt2=elementa, color=255, thickness=5)
                lineting = element
            else:
                lineting = element
                firsthit = True

        # we draw the circles where we found them.
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, 125, 4)

    return np.vstack([image, output])
