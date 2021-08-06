from typing import List

import PyQt5.QtGui
import numpy as np

import classes.class_frameclass
import functions.image_processing.image_process
from functions.image_processing.image_process import change_qpix as cqpx


class MovieClass:
    framelist: List[classes.class_frameclass.FrameClass]

    # https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects
    # # Callers can only provide two parameters and optionally pass _cache by keyword
    # def expensive(arg1, arg2, *, _cache={}):
    #     if (arg1, arg2) in _cache:
    #         return _cache[(arg1, arg2)]
    #
    #     # Calculate the value
    #     result = ... expensive computation ...
    #     _cache[(arg1, arg2)] = result           # Store result in the cache
    #     return result

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
        self.framelist.clear()  # in case of re-initialization empty the previous list.
        for element in imlist:
            # EMBARRASSINGLY PARALLEL, OR NOT!?!
            # For the life of me I can not figure out how to share a class between different processes. Queues,
            # managers, proxies. Not working. Problem is pickling. Besides it being SO slow, it does not support
            # QPix stuff. I need to find a way to use some form of shared memory.
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
        # print("current frame is: " + str(self.currentframe))

    def return_frame(self):
        # print("return called")
        # print(self.parameters['gls'])
        self.cframe = self.framelist[self.currentframe]  # cframe for [c]urrent frame
        cframe = self.cframe
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
        if 'g_filter2' in self.parameters:
            self.filters['g_filter2'] = functions.image_processing.image_process.gaus_filter(
                self.parameters['shape'], self.parameters['g_filter2'][1], self.parameters['g_filter2'][2],
                self.parameters['g_filter2'][3])

    def edge_call(self):
        return self.cframe.call_edge(self.parameters['sobel'], self.parameters['canny'])

    def edge_call2(self):
        return self.cframe.canny2(self.parameters['canny2'][1:])
        # return self.cframe.sobel2(self.parameters['sobel2'][1:])

    def morphstart(self, textstring):
        print("morphstart")
        # i feel this alias could be .self
        cframe = self.framelist[self.currentframe]
        return cframe.domorph(textstring)

    def get_og_frame(self):
        return self.cframe.frames['original']

    def call_flood(self, coords):
        return self.cframe.call_flood(coords)

    def circlefind(self):
        return self.cframe.circlefind(self.parameters['hough'])

    def gls2(self):
        if 'gls2' in self.parameters:
            return self.cframe.calc_gls2(self.parameters['gls2'])
        else:
            return self.cframe.qpix['original']

    def gfilter2(self):
        return self.cframe.calc_gfilter2(self.filters['g_filter2'])
