# PARALLEL BABY
import multiprocessing
from multiprocessing.managers import BaseManager

import PyQt5.QtGui
import numpy as np

import classes.class_frameclass
import functions.image_processing.image_process
from functions.image_processing.image_process import change_qpix as cqpx


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


def external_worker(queue, my_list, private_q):
    """"
    list: is a list containing tuples [(idx,val), (idx,val) ... ], where each element has an index and a tuple.
    """
    manager = MyManager()
    manager.start()
    classlist = []

    for idx, val in my_list:
        created = manager.frameclass(val)
        # created = classes.class_frameclass.FrameClass(val)
        classlist.append((idx, created))

    queue.put(classlist)

    while True:
        if private_q.empty() is False:
            msg = private_q.get()
            if msg == "stop":
                print("process exiting")
                manager.shutdown()
                break


def internal_worker(my_list):
    returnlist = []
    for idx, val in my_list:
        created = classes.class_frameclass.FrameClass(val)
        returnlist.append((idx, created))
    return returnlist


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
        processes = []
        classlist = []
        self.framelist.clear()  # in case of re-initialization empty the previous list.
        imlist_numbered = [x for x in enumerate(imlist)]
        imlist_chopped = get4(imlist_numbered)

        q = multiprocessing.Queue()
        qlist = [multiprocessing.Queue(), multiprocessing.Queue(), multiprocessing.Queue()]

        print(imlist_chopped)

        for x in range(3):  # [0,1,2]
            p = multiprocessing.Process(target=external_worker, args=(q, imlist_chopped[x], qlist[x]))
            p.start()
            processes.append(p)

        print("defined")
        classlist.append(internal_worker(imlist_chopped[3]))
        print(classlist)

        while len(classlist) <3:
            preclasslist = q.get()
            print("did we get here?")
            temp = [(x, y._getvalue()) for x, y in preclasslist]
            classlist.append(temp)

        for element in qlist:
            element.put("stop")

        print(classlist)
        # OLD stuff happening below

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
