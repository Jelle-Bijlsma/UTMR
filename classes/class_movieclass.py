# PARALLEL BABY
import multiprocessing
from multiprocessing.managers import BaseManager

import PyQt5.QtGui
import numpy as np

import classes.class_frameclass
import functions.image_processing.image_process
from functions.image_processing.image_process import change_qpix as cqpx

import time

def get4(list_input):
    def correct(val, val2=1):
        # in essence (value1*lenght)/value2
        return int(np.floor(val2 * len(list_input)) / val)

    newlist = []
    #  1
    iteration = list_input[0:correct(4)]
    newlist.append(iteration)
    #  2
    iteration = list_input[correct(4) + 1:correct(2)]
    newlist.append(iteration)
    #  3
    iteration = list_input[correct(2) + 1:correct(4, 3)]
    newlist.append(iteration)
    #  4
    iteration = list_input[correct(4, 3) + 1:len(list_input)]
    newlist.append(iteration)

    return newlist


class MyManager(BaseManager):
    pass


MyManager.register('frameclass', classes.class_frameclass.FrameClass)


def worker(my_list):
    for element in my_list:
        element.init2()


class MovieClass:
    def __init__(self):
        self.currentframe = 0
        self.maxframes = int
        self.framelist = []
        self.parameters = {'gls': [0, 0, 0, 0], 'b_filter': [False, 1, 0], 'shape': (0, 0),
                           'g_filter': [False, 0, 0]}
        # the parameters can be explained as follows
        # gls:          brightness[0] boost[1]  lbound[2]  rbound[3]
        # b_filter:     on/off [0] cutoff [1] order [2]
        # shape:        size of the frames (x,y)
        self.filters = {'b_filter': np.array([]), 'g_filter': np.array([])}
        self.qpix = {'b_filter': cqpx(np.array([])), 'g_filter': cqpx(np.array([]))}

    def create_frameclass(self, imlist):
        """"
        Imlist: list of all the frames (np.array) ordered
        Framelist: List of all the instances of the frameclass, ordered.

        """

        manager = MyManager()
        manager.start()

        classlist = []
        rn = []

        for element in imlist:
            classlist.append(manager.frameclass(element))

        processes = []

        self.framelist.clear()  # in case of re-initialization empty the previous list.
        chop_classlist = get4(classlist)

        for x in range(3):  # [0,1,2]
            p = multiprocessing.Process(target=worker, args=(chop_classlist[x],))
            p.start()
            processes.append(p)

        worker(chop_classlist[3])

        for x in processes:
            x.join()
        # OLD stuff happening below

        for element in classlist:
            rn.append(element._getvalue())

        print("end")
        time.sleep(10)

        for element in imlist:
            # EMBARRASSINGLY PARALLEL, setup thread workers soon.
            # or is it? Require class objects to be sent from
            self.framelist.append(classes.class_frameclass.FrameClass(element))
        self.maxframes = len(imlist) - 1
        self.parameters['shape'] = self.framelist[self.maxframes].parameters['shape']
        # (370, 370) for current call
        self.getnewbfilter()

    def next_frame(self):
        if self.currentframe == self.maxframes:
            self.currentframe = 0
        else:
            self.currentframe += 1
        print("current frame is: " + str(self.currentframe))

    def return_frame(self):
        print("return called")
        print(self.parameters['gls'])
        cframe = self.framelist[self.currentframe]  # cframe for [c]urrent frame
        cframe.return_info(self.parameters['gls'], self.parameters['b_filter'][0], self.filters['b_filter'],
                           self.parameters['g_filter'][0], self.filters['g_filter'])
        return cframe.qpix['main'], cframe.histogram, cframe.qpix['fft'], self.qpix['b_filter'], self.qpix['g_filter']

    def getnewbfilter(self):
        # the filter is 'good looking' meaning it is centered aesthetically.
        self.filters['b_filter'] = functions.image_processing.image_process.butter_filter(
            self.parameters['shape'], self.parameters['b_filter'][1], self.parameters['b_filter'][2])
        self.qpix['b_filter'] = cqpx(self.filters['b_filter'])

    def getnewgfilter(self):
        self.filters['g_filter'] = functions.image_processing.image_process.gaus_filter(
            self.parameters['shape'], self.parameters['g_filter'][1], self.parameters['g_filter'][2],
            self.parameters['g_filter'][3])
        self.qpix['g_filter'] = cqpx(self.filters['g_filter'])

    def edge_call(self, para_sobel: list, para_canny: list) -> (PyQt5.QtGui.QPixmap, PyQt5.QtGui.QPixmap):
        return self.framelist[self.currentframe].call_edge(para_sobel, para_canny)
