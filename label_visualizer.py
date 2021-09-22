import math
import pickle
import os
import cv2


class Point:
    """"
    Point is a class which can be created by the PointCollector. It tracks it position in X,Y.
    It can remember its position when using the 'update' method, and using check, it can check if the given coordinate
    is in range of the current state. if it is, it will update the current state.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xtrail = []
        self.ytrail = []
        self.active = True
        self.framelist = []

    def update(self, x, y):
        self.xtrail.append(self.x)
        self.ytrail.append(self.y)
        self.x = x
        self.y = y

    def check(self, coordtuple, frame):
        x, y, _ = coordtuple
        distance = math.dist((x, y), (self.x, self.y))
        if distance < 10:
            self.update(x, y)
            self.framelist.append(frame)
            return True
        else:
            return False


class PointCollector:
    """"
    PointCollector is created to handle an unorganized list of coordinates. Given a list of coordinates, using the
    'step' method, it will check if any of the given points fit the profile of Points in the 'activepoints' list.
    If not, the Points are created. During a 'step' call, if an element of 'activepoints' has no hit, it will be placed
    in the 'passivepoints' group.
    """

    def __init__(self):
        print("you have summoned the PointCollector")
        self.activepoints = []
        self.passivepoints = []
        self.stepsdone = -1
        self.allpoints = []

    def step(self, coordlist):
        self.stepsdone += 1
        print(self.stepsdone)
        self.checkactive()  # check which points are still on screen

        # iterate over every active point to see if the new points are close to them
        for point in self.activepoints:
            found = False
            for coord in coordlist:  # check which coord belongs to the point
                if point.check(coord, self.stepsdone):
                    found = True
                    break
            # <-- from break go here
            if found is True:
                coordlist.remove(coord)  # coord is claimed by the point and can be removed
            elif found is False:
                print(f"removed a point: {point.x, point.y}")  # point is unused, make it passive
                point.active = False
            else:
                # throw an error if this case occurs
                a = 5 / 0

        # if not assigned to a Point, create one.
        for element in coordlist:
            x, y, _ = element
            print(f"created a point {x, y}")
            self.allpoints.append(Point(x, y))

    def checkactive(self):
        self.activepoints = []
        self.passivepoints = []

        for point in self.allpoints:
            if point.active:
                self.activepoints.append(point)
            else:
                self.passivepoints.append(point)


def show_full(images, malist):
    """"
    Displays a video which overlays the given point position with a circle on the original footage.
    """
    for img, coords in zip(images, malist):
        for coord in coords:
            coordxy = coord[:-1]
            coordxy = (int(coordxy[0]), int(coordxy[1]))
            cv2.circle(img, coordxy, 8, 255, 1)
        cv2.imshow('window', img)
        k = cv2.waitKey(100)
        if k == 27:
            return


def show_part(images, point: Point):
    # had to do some hocuspocus here. Used a zip(images,xtrail,ytrail) first, before i realized that
    # the length difference in trail with images was causing a problem. This, for some particular reason, did not
    # give ANY error, or warning. it just took the first images in the list.

    # showpart is a display function which visualizes how poorly the magnetic markers are visible.
    counter = 0
    for frame in range(len(images)):
        try:
            if point.framelist[counter] == frame:
                x = int(point.xtrail[counter])
                y = int(point.ytrail[counter])
                off = 20  # size of the window
                window = images[frame][y - off:y + off, x - off:x + off]
                scale = 20  # upscale the image to make it more visible
                width = int(window.shape[1] * scale)
                height = int(window.shape[0] * scale)
                window = cv2.resize(window, (width, height), interpolation=cv2.INTER_NEAREST)
                cv2.imshow('window', window)
                # if escape pressed, skip
                counter += 1
                k = cv2.waitKey(100)
                if k == 27:
                    return
                # if space pressed, pause
                if k == 32:
                    a = cv2.waitKey(100000)
                    if a == 32:
                        continue
        except IndexError:
            pass


# create the pointcollector and  load in all the selected points
pc = PointCollector()
#path = "./data/keypoints_mri31.pcl"
#path = "./data/keypoints_mri_32.pcl"
#path = "./data/keypoints_mri_blur.pcl"
path = "./data/keypoints_mri_stationary.pcl"

file = open(path, 'rb')
malist, _ = pickle.load(file)
file.close()

# create an 'images' list which hosts all the original footage
images = []
#png_path = "./data/png/mri31/"
#png_path = "./data/png/mri32/"
#png_path = "./data/png/0315_moving_blur/"
png_path = "./data/png/0313_stationary/"

png_files = os.listdir(png_path)
png_files = sorted(png_files)
for element in png_files:
    fp = png_path + element
    images.append(cv2.imread(fp, 0))

show_full(images, malist)

# run the pointcollector over every frame
for item in malist:
    pc.step(item)

# display the results of the pointcollector
for element in pc.allpoints:
    show_part(images, element)
