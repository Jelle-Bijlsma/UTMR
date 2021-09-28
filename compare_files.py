import copy
import math
import pickle
import os
import cv2
from matplotlib import pyplot as plt


# from label_visualizer import PointCollector
# file = open('./data/pointcollector.pcl', 'rb')
# pc: PointCollector = pickle.load(file)
# print(type(pc))

class Point:
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
    def __init__(self,measured,true):
        self.measured: list = measured
        self.true: list = true
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
            if range > 10:
                break
            mcoord = coords[1]
            pointnum = coords[2]
            self.pointlist[pointnum].assign(mcoord)
            clonglist = copy.deepcopy(self.longlist)
            for element in clonglist:
                #print(f"this is element = {element}")
                #print(element[0])
                if (mcoord == element[1]) or (pointnum == element[2]):
                    #print("we do this?")
                    self.longlist.remove(element)
        # self longlist now contains double points still
        self.misplaced = []
        for element in self.longlist:
            if element[1] not in self.misplaced:
                self.misplaced.append(element[1])


    def assornot(self):
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

if __name__ == "__main__":

    #file = open('./data/keypoints_mri31.pcl', 'rb')
    file = open('./data/keypoints_mri_32.pcl', 'rb')
    pre_truecoordlist, _ = pickle.load(file)
    file.close()

    # file = open('./data/measured_mri31', 'rb')
    file = open('./data/measured_mri32', 'rb')
    pre_measured, offset = pickle.load(file)
    file.close()

    images = []
    # png_path = "./data/png/mri31/"
    png_path = "./data/png/mri32/"
    # png_path = "./data/png/0315_moving_blur/"
    # png_path = "./data/png/0313_stationary/"

    png_files = os.listdir(png_path)
    png_files = sorted(png_files)
    for element in png_files:
        fp = png_path + element
        images.append(cv2.imread(fp, 1))
    #file = open('./data/png/mri31/','rb')


    truecoordlist = []
    for clist in pre_truecoordlist:
        # remove brightness
        clist_new = []
        for coord in clist:
            clist_new.append((coord[0], coord[1]))
        truecoordlist.append(clist_new)

    measured = []
    for element in pre_measured:
        measured.append(element[0])

    offset = (offset[0], offset[2])
    #print(offset)
    measured_noff = []
    for frame in measured:
        newframe = []
        for coordinate in frame:
            newframe.append((coordinate[0]+offset[0], coordinate[1]+offset[1]))
        measured_noff.append(newframe)

    #print(len(truecoordlist))
    #print(len(measured_noff))

    true = truecoordlist
    dc = DistComp(measured_noff[0],true[0])
    dc.point_battle()
    dc.assornot()
    ass, noass,faulty = dc.final_answer()

    # B G R
    green = (0,255,0)       # correctly assessed
    yellow = (0,255,255)    # missed
    red = (0,0,255)         # not a real point


    print(f"assigned: {ass}")
    print(f"not assigned: {noass}")
    print(f"faulty: {faulty}")

    big_ass = []
    big_noass = []
    big_faulty = []

    print(len(measured_noff))
    print(len(true))

    for image,index in zip(images,range(len(images))):
        #print(index)
        dc = DistComp(measured_noff[index], true[index])
        dc.point_battle()
        dc.assornot()
        ass, noass, faulty = dc.final_answer()

        big_ass.append(ass)
        big_noass.append(noass)
        big_faulty.append(faulty)

        for element in ass:
            #print(f"element.coord = {element.coord}")
            cv2.circle(image,element.coord,3,green)
        for element in noass:
            cv2.circle(image,element.coord,3,yellow)
        for element in faulty:
            cv2.circle(image,element,3,red)

        cv2.imshow('hi',image)
        cv2.waitKey(0)

    plotting = True
    if plotting is True:
        ltrue = len(true)
        pvar1 = []
        pvar2 = []
        pvar3 = []
        pvar4 = []
        for ba,faulty,tr in zip(big_ass, big_faulty,true):
            pvar1.append(len(ba))
            pvar4.append(len(tr))
            total = 0
            for element in ba:
                total += element.distance
            if len(ba) != 0:
                pvar2.append(total/len(ba))
            else:
                pvar2.append(0)
            pvar3.append(len(faulty))

        print(f"pvar1 = {pvar1}")
        print(f"pvar2 = {pvar2}")
        print(f"pvar3 = {pvar3}")
        print(f"pvar4 = {pvar4}")

        i = range(len(pvar1))
        plt.plot(i,pvar1)
        plt.plot(i,pvar2)
        plt.plot(i,pvar3)
        plt.plot(i,pvar4)
        plt.legend(['assigned', 'avg distance', 'total faults', 'true points'])
        plt.show()
