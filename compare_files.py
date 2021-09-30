import copy
import math
import pickle
import os
import scipy.stats as stats

import cv2
import numpy as np
from matplotlib import pyplot as plt

""""
This function compares the 'measured results' which are obtained by the program, with the 'true results' which are
obtained by human selection. Green points are points whitin the 'maxdist' or maximum distance range, yellow points are
points the program missed, and red points are mislabeled points.

Continue to the next frame with spacebar 
"""

class Point:
    """
    Point is a class for each true value. It can bind to a measured value using 'assign' method. The instances of
    Point are controlled by 'DistComp'.
    """
    def __init__(self, coord, pnum):
        self.coord: tuple = (int(coord[0]),int(coord[1]))
        self.x = coord[0]
        self.y = coord[0]
        self.name = pnum
        self.rangelist = []
        self.assigned = False

    def calc_dist(self,coord):
        self.rangelist.append((math.dist(self.coord,coord),coord,self.name))

    def assign(self,coord):
        self.mcoord = coord
        self.assigned = True
        self.distance = math.dist(self.coord,self.mcoord)

class DistComp:
    """
    DistComp or Distance Computer is called for each frame to solve the problem of assigning a measured value to a
    true value. How do we know a measured value corresponds to a true value? Multiple conflicting scenario's exist:
        - There could be two measured points (MP) for one true value (TV).
        - There could be no measured point for a true value.
        - There could be no true value for a measured point.

    DistComp allows MPs to fight for TVs. TVs are all made into Point instances (__init__), and the distance from each
    TV to each MP is calculated, and the distances are sorted (calc_truedist) and pooled into 'self.longlist'.
    In 'point_battle' we find the MP that has the closest distance to a specific TV, now we can pop that value from
    the longlist and assign the MP to the TV. We continue this process until there are no elements in the longlist
    that are < maxdist. Any unassigned TV is considered a miss, and any unassigned MP is considered falsely measured.

    """
    def __init__(self,measured,truelist: list):
        self.maxdist = 10  # if two points have a larger distance than 'max(imum) dist(ance), it is rejected as a
        # candidate.
        self.measured: list = measured
        self.true: list = truelist
        self.pointlist = []
        for point_coord, numb in zip(self.true, range(len(self.true))):
            self.pointlist.append(Point(point_coord,numb))
        self.calc_truedist()

    def calc_truedist(self):
        self.longlist = []
        for point in self.pointlist:
            for coord in self.measured:
                point.calc_dist(coord)
            point.rangelist = sorted(point.rangelist)
            self.longlist.extend(point.rangelist)

    def point_battle(self):
        # longlist is the list of all the official coordinates, and the distance from them to the measured
        # points.
        pickfirst = lambda x : x[0]
        self.longlist = sorted(self.longlist, key=pickfirst)
        while True:
            try:
                coords = self.longlist[0]
            except IndexError:
                break
            range = coords[0]
            if range > self.maxdist:
                break
            mcoord = coords[1]
            pointnum = coords[2]
            self.pointlist[pointnum].assign(mcoord)
            clonglist = copy.deepcopy(self.longlist)
            for element in clonglist:
                if (mcoord == element[1]) or (pointnum == element[2]):
                    self.longlist.remove(element)
        # self longlist now contains double points still
        self.misplaced = []
        for element in self.longlist:
            if element[1] not in self.misplaced:
                self.misplaced.append(element[1])

    def assornot(self):
        """"
        ass(igned) or not: Checks if all the TVs are assigned. Put the TVs in two lists, assigned/unassigned.
        """
        self.assigned = []
        self.unassigned = []
        for element in self.pointlist:
            if element.assigned:
                self.assigned.append(element)
            else:
                self.unassigned.append(element)

    def final_answer(self):
        return (self.assigned, self.unassigned, self.misplaced)

    def give_rangelist(self):
        for element in self.pointlist:
            print(element.rangelist)

def show_movie(images, malist, coleur):
    """"
    Displays a video which overlays the given point position with a circle on the original footage.
    """
    for img, coords in zip(images, malist):
        for coord in coords:
            cv2.circle(img, coord, 8, coleur, 1)
        cv2.imshow('window', img)
        k = cv2.waitKey(100)
        if k == 27:
            return

def load_pngs(png_path):
    # load in the PNG's
    images = []
    png_files = os.listdir(png_path)
    png_files = sorted(png_files)
    for element in png_files:
        fp = png_path + element
        images.append(cv2.imread(fp, 1))
    return images

def generate_data(trial_num, plotting,video):
    green = (0, 255, 0)  # correctly assessed
    yellow = (0, 255, 255)  # missed
    red = (0, 0, 255)  # not a real point

    truecoordlist: list = []  # removes brightness (b): (x,y,b) -> (x,y)
    measured_noff: list = []  # stores translated measured points, compensate for cut-out

    # dependant on which set you will be using
    truecoord_path = f'./data/keypoints_mri{trial_num}.pcl'
    file = open(truecoord_path, 'rb')
    pre_truecoordlist, _ = pickle.load(file)
    file.close()
    measured_path = f'./data/measured_mri{trial_num}.pcl'
    file = open(measured_path, 'rb')
    pre_measured, offset = pickle.load(file)
    file.close()
    png_path = f"./data/png/mri{trial_num}/"
    images = load_pngs(png_path)

    # remove brightness
    for clist in pre_truecoordlist:
        clist_new = []
        for coord in clist:
            clist_new.append((coord[0], coord[1]))
        truecoordlist.append(clist_new)

    # the output from UTMR_main2 is a list in a list, so we peal one layer off in this step
    measured = [x[0] for x in pre_measured]
    offset = (offset[0], offset[2])  # we cut off the pictures partially in main, this compensates
    # for the cutoff.
    for frame in measured:
        newframe = []
        for coordinate in frame:
            newframe.append((coordinate[0] + offset[0], coordinate[1] + offset[1]))
        measured_noff.append(newframe)

    big_ass = []  # contains all the assigned points
    big_noass = []  # contains the missed points
    big_faulty = []  # contains the faulty points

    # do the calc:

    for image, index in zip(images, range(len(images))):
        dc = DistComp(measured_noff[index], truecoordlist[index])
        dc.point_battle()
        dc.assornot()
        ass, noass, faulty = dc.final_answer()

        big_ass.append(ass)
        big_noass.append(noass)
        big_faulty.append(faulty)

        for element in ass:
            cv2.circle(image, element.coord, 3, green)
        for element in noass:
            cv2.circle(image, element.coord, 3, yellow)
        for element in faulty:
            cv2.circle(image, element, 3, red)

        if video is True:
            cv2.imshow('hi', image)
            cv2.waitKey(0)

    # generate the end plots
    pvar1 = []
    pvar2 = []
    pvar3 = []
    pvar4 = []

    for ba, faulty, tr in zip(big_ass, big_faulty, truecoordlist):
        pvar1.append(len(ba))
        pvar4.append(len(tr))
        total = 0
        for element in ba:
            total += element.distance
        if len(ba) != 0:
            pvar2.append(total / len(ba))
        else:
            pvar2.append(0)
        pvar3.append(len(faulty))

    i = range(len(pvar1))
    plt.plot(i, pvar1)
    plt.plot(i, pvar2)
    plt.plot(i, pvar3)
    plt.plot(i, pvar4)
    plt.legend(['assigned', 'avg distance', 'total faults', 'true points'])
    if plotting is True:
        plt.show()

    # print(pvar2)
    import statistics
    da_mean = statistics.mean(pvar2)
    da_sd = statistics.stdev(pvar2)
    return da_mean,da_sd, pvar2

if __name__ == "__main__":
    mean1, sd1, res1 = generate_data(31,plotting=True,video=False)
    mean2, sd2, res2, = generate_data(32, plotting=True, video=False)

    print(f"Standard deviation run31: {sd1}, mean: {mean1}")
    print(f"Standard deviation run32: {sd2}, mean: {mean2}")

    res1= np.array(res1)
    rmsq1 = (np.sum(res1**2)**0.5)/len(res1)
    res2 = np.array(res2)
    rmsq2 = (np.sum(res2**2)**0.5)/len(res2)

    mae1 = np.max(res1)
    mae2 = np.max(res2)

    print(f"RMSQ of run31: {rmsq1}, MAE: {mae1}")
    print(f"RMSQ of run32: {rmsq2}, MAE: {mae2}")

    swq1 = stats.shapiro(res1)
    swq2 = stats.shapiro(res2)

    print(f"Shapiro Wilkes of run31: {swq1}")
    print(f"Shapiro Wilkes of run32: {swq2}")

    ttest1 = stats.ttest_rel(res1,res2)
    print(f"t-test value of run31 & run32: {ttest1}")